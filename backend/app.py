import os
import datetime
import time
from functools import wraps
from urllib.parse import urlparse
from quart import Quart, request, jsonify, send_from_directory, make_response
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit, RateLimit
from quart_rate_limiter.store import RateLimiterStoreABC
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re
import logging
import uuid
import html
import stripe
import razorpay
from marshmallow import ValidationError
import pyotp
import qrcode
from io import BytesIO
import base64
from beanie import init_beanie
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from cryptography.fernet import Fernet
from dotenv import load_dotenv  # type: ignore
import time
from arq import create_pool
from arq.connections import RedisSettings

load_dotenv()

fernet_key = os.environ.get('FERNET_KEY', Fernet.generate_key().decode('utf-8'))
cipher_suite = Fernet(fernet_key.encode('utf-8'))

def encrypt_pii(data: str) -> str:
    if not data:
        return data
    return cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_pii(data: str) -> str:
    if not data:
        return data
    try:
        return cipher_suite.decrypt(data.encode('utf-8')).decode('utf-8')
    except Exception:
        # Fallback if the data wasn't encrypted (e.g. legacy data)
        return data

from models import User, Cart, Order, Product, RestaurantTable, Employee, RevokedToken, BlogPost, NewsletterSubscriber, AuditLog

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_mock_key')
razorpay_client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_mock'), os.environ.get('RAZORPAY_KEY_SECRET', 'mock_secret')))

def load_secret_key():
    env_key = os.environ.get('CAFE_SECRET_KEY')
    if env_key:
        return env_key
    if os.environ.get('VERCEL'):
        secret_path = '/tmp/secret.key'
    else:
        secret_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.key')
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
    new_key = os.urandom(24).hex()
    with open(secret_path, 'w') as f:
        f.write(new_key)
    return new_key

app = Quart(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend')))
app = cors(app, allow_origin="*")
app.config['SECRET_KEY'] = load_secret_key()

# Ensure DATABASE_URL is explicitly set, fallback to sqlite if missing to avoid hardcoded credentials
DB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

redis_client = None
arq_pool = None

class RedisRateLimiterStore(RateLimiterStoreABC):
    async def before_serving(self) -> None:
        pass
        
    async def after_serving(self) -> None:
        pass

    async def get(self, key: str, default: datetime.datetime) -> datetime.datetime:
        if not redis_client:
            return default
            
        val = await redis_client.get(key)
        if val:
            return datetime.datetime.fromisoformat(val)
        return default

    async def set(self, key: str, tat: datetime.datetime) -> None:
        if redis_client:
            # TTL of 1 hour is a safe default for GCRA TAT caching
            await redis_client.set(key, tat.isoformat(), ex=3600)

limiter = RateLimiter(app, store=RedisRateLimiterStore())

@app.before_serving
async def init_db():
    global redis_client
    global arq_pool
    
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    arq_pool = await create_pool(RedisSettings.from_dsn(REDIS_URL))
    
    client = AsyncIOMotorClient(DB_URL)
    await init_beanie(database=client.boojee, document_models=[User, Cart, Order, Product, RestaurantTable, Employee, RevokedToken, BlogPost, NewsletterSubscriber, AuditLog])
    
    # Initialize mock data
    if await Product.find_all().count() == 0:
        await Product.insert_many([
            Product(name='House Espresso', description='Built around seasonal lots.', price=120, category='coffee', image_url='images/menu-espresso.png'),
            Product(name='Americano', description='Carefully calibrated extraction.', price=130, category='coffee', image_url='images/menu-americano.png'),
            Product(name='Flat White', description='Balanced for sweetness and clarity.', price=150, category='coffee', image_url='images/menu-flat-white.png'),
            Product(name='Oat Flat White', description='Oat milk variant.', price=170, category='coffee', image_url='images/menu-oat-flat-white.png'),
            Product(name='Cappuccino', description='Classic cappuccino.', price=160, category='coffee', image_url='images/menu-cappuccino.png'),
            Product(name='Filter of the Day', description='Daily special.', price=140, category='coffee', image_url='images/menu-filter-coffee.png'),
            Product(name='Mocha', description='Chocolate infused coffee.', price=180, category='coffee', image_url='images/menu-mocha.png'),
            Product(name='Velvet Hot Chocolate', description='Silky hot chocolate.', price=200, category='tea', image_url='images/Cup-of-Hot-Chocolate.png'),
            Product(name='Garden Strawberry Tart', description='Fresh strawberries.', price=250, category='sweet', image_url='images/Strawberry-Tarts.png'),
            Product(name='Dark Chocolate Cookie', description='Rich and soft.', price=150, category='sweet', image_url='images/Cookies.png')
        ])
        
    if await RestaurantTable.find_all().count() == 0:
        await RestaurantTable.insert_many([
            RestaurantTable(table_number=str(i), status='available', capacity=4) for i in range(1, 11)
        ])

@app.after_serving
async def close_db():
    pass

@app.before_request
async def csrf_protect():
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        if not request.path.startswith('/api/'):
            return
            
        if app.config.get('TESTING'):
            return
            
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        expected_host = request.host
        
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.netloc != expected_host:
                return jsonify({'message': 'CSRF verification failed (Origin mismatch)'}), 403
        elif referer:
            parsed_referer = urlparse(referer)
            if parsed_referer.netloc != expected_host:
                return jsonify({'message': 'CSRF verification failed (Referer mismatch)'}), 403
        else:
            return jsonify({'message': 'CSRF verification failed (Origin/Referer missing)'}), 403

@app.errorhandler(Exception)
async def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    return jsonify({'message': 'An internal server error occurred.'}), 500

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")

@app.after_request
async def apply_security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = request.cookies.get('boojee_token')
        
        if not token:
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Check if revoked in Redis (skip if Redis is not connected during tests)
            is_revoked = False
            if redis_client:
                is_revoked = await redis_client.get(f"revoked_{data.get('jti')}")
            
            if is_revoked:
                return jsonify({'message': 'Token has been revoked.'}), 401
            
            user = await User.get(data['user_id'])
            if not user:
                raise Exception("User not found")
        except Exception as e:
            app.logger.warning(f"Invalid token attempt: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return await f(user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    async def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin privileges required!'}), 403
        return await f(current_user, *args, **kwargs)
    return token_required(decorated)

from schemas import RegisterSchema, LoginSchema, OnboardingSchema, CartSchema, CheckoutSchema, NewsletterSchema, MFAVerifySchema, MFALoginSchema

@app.route('/api/register', methods=['POST'])
@rate_limit(5, datetime.timedelta(minutes=1))
async def register():
    try:
        data = RegisterSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    email = data['email'].lower()
    password = data['password']
        
    hashed_password = generate_password_hash(password, method='scrypt')
    
    if await User.find_one(User.email == email) is not None:
        app.logger.warning(f"Registration failed: Email {email} already exists")
        return jsonify({'message': 'User already exists'}), 409
        
    new_user = User(email=email, password=hashed_password)
    await new_user.insert()
    
    app.logger.info(f"New user registered: {email}")
    
    jti = str(uuid.uuid4())
    access_token = jwt.encode({'user_id': str(new_user.id), 'jti': jti, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode({'user_id': str(new_user.id), 'jti': jti, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7), 'type': 'refresh'}, app.config['SECRET_KEY'], algorithm='HS256')
    
    resp = await make_response(jsonify({'message': 'Welcome to Boojee Cafe.', 'user': {'email': email, 'role': 'customer'}}))
    resp.set_cookie('boojee_token', access_token, httponly=True, secure=True, samesite='Strict', max_age=15*60)
    resp.set_cookie('boojee_refresh', refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7*24*60*60)
    return resp, 201

@app.route('/api/login', methods=['POST'])
@rate_limit(5, datetime.timedelta(minutes=1))
async def login():
    try:
        data = LoginSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    email = data['email'].lower()
    password = data['password']
    
    user = await User.find_one(User.email == email)
    
    if not user or not check_password_hash(user.password, password):
        app.logger.warning(f"Failed login attempt for email: {email}")
        return jsonify({'message': 'Invalid credentials'}), 401
        
    if user.mfa_enabled:
        app.logger.info(f"MFA required for user: {user.id}")
        mfa_token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
            'type': 'mfa_pending'
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'MFA required', 'mfa_required': True, 'mfa_token': mfa_token}), 200

    app.logger.info(f"Successful login for user: {user.id}")
        
    jti = str(uuid.uuid4())
    access_token = jwt.encode({
        'user_id': str(user.id),
        'jti': jti,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    refresh_token = jwt.encode({
        'user_id': str(user.id),
        'jti': jti,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'type': 'refresh'
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    resp = await make_response(jsonify({'user': {'email': user.email, 'role': user.role}}))
    resp.set_cookie('boojee_token', access_token, httponly=True, secure=True, samesite='Strict', max_age=15*60)
    resp.set_cookie('boojee_refresh', refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7*24*60*60)
    return resp, 200

@app.route('/api/login/mfa', methods=['POST'])
@rate_limit(5, datetime.timedelta(minutes=1))
async def login_mfa():
    try:
        data = MFALoginSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    try:
        token_data = jwt.decode(data['mfa_token'], app.config['SECRET_KEY'], algorithms=['HS256'])
        if token_data.get('type') != 'mfa_pending':
            raise Exception("Invalid token type")
        user = await User.get(token_data['user_id'])
        if not user or not user.mfa_enabled:
            raise Exception("Invalid user or MFA not enabled")
    except Exception as e:
        app.logger.warning(f"Invalid MFA token attempt: {e}")
        return jsonify({'message': 'Invalid or expired MFA token'}), 401
        
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(data['code']):
        return jsonify({'message': 'Invalid MFA code'}), 401
        
    app.logger.info(f"Successful MFA login for user: {user.id}")
        
    jti = str(uuid.uuid4())
    access_token = jwt.encode({'user_id': str(user.id), 'jti': jti, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode({'user_id': str(user.id), 'jti': jti, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7), 'type': 'refresh'}, app.config['SECRET_KEY'], algorithm='HS256')
    
    resp = await make_response(jsonify({'user': {'email': user.email, 'role': user.role}}))
    resp.set_cookie('boojee_token', access_token, httponly=True, secure=True, samesite='Strict', max_age=15*60)
    resp.set_cookie('boojee_refresh', refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7*24*60*60)
    return resp, 200

@app.route('/api/refresh', methods=['POST'])
async def refresh():
    refresh_token = request.cookies.get('boojee_refresh')
    if not refresh_token:
        return jsonify({'message': 'Refresh token missing'}), 401
        
    try:
        data = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if data.get('type') != 'refresh':
            raise Exception("Invalid token type")
            
        is_revoked = False
        if redis_client:
            is_revoked = await redis_client.get(f"revoked_{data.get('jti')}")
            
        if is_revoked:
            raise Exception("Token revoked")
            
        user = await User.get(data['user_id'])
        if not user:
            raise Exception("User not found")
            
        # Issue new access token
        new_access = jwt.encode({
            'user_id': str(user.id),
            'jti': data.get('jti'), # Keep same jti or rotate, keeping same for simplicity
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        resp = await make_response(jsonify({'message': 'Token refreshed'}))
        resp.set_cookie('boojee_token', new_access, httponly=True, secure=True, samesite='Strict', max_age=15*60)
        return resp, 200
    except Exception as e:
        app.logger.warning(f"Invalid refresh attempt: {e}")
        return jsonify({'message': 'Invalid refresh token'}), 401

@app.route('/api/logout', methods=['POST'])
@token_required
async def logout(current_user):
    token = request.cookies.get('boojee_token')
    if not token and 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(' ')[1]
        
    if not token:
        return jsonify({'message': 'Successfully logged out.'}), 200
        
    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'], options={"verify_exp": False})
    
    # Calculate remaining time for the token to set accurate TTL in Redis
    exp_timestamp = data.get('exp', 0)
    current_time = datetime.datetime.utcnow().timestamp()
    ttl = int(exp_timestamp - current_time)
    if ttl <= 0:
        ttl = 3600 # fallback
        
    if redis_client:
        await redis_client.setex(f"revoked_{data.get('jti')}", ttl, "1")
    
    response = jsonify({'message': 'Successfully logged out.'})
    response.delete_cookie('boojee_token')
    response.delete_cookie('boojee_refresh')
    return response, 200

@app.route('/api/mfa/setup', methods=['POST'])
@token_required
async def mfa_setup(current_user):
    if current_user.mfa_enabled:
        return jsonify({'message': 'MFA is already enabled.'}), 400
        
    secret = pyotp.random_base32()
    current_user.mfa_secret = secret
    await current_user.save()
    
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name="Boojee Cafe")
    
    qr = qrcode.make(uri)
    buffered = BytesIO()
    qr.save(buffered, "PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return jsonify({
        'secret': secret,
        'qr_code': f"data:image/png;base64,{qr_base64}"
    }), 200

@app.route('/api/mfa/verify', methods=['POST'])
@token_required
async def mfa_verify(current_user):
    if current_user.mfa_enabled:
        return jsonify({'message': 'MFA is already enabled.'}), 400
        
    try:
        data = MFAVerifySchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    if not current_user.mfa_secret:
        return jsonify({'message': 'MFA setup not initiated.'}), 400
        
    totp = pyotp.TOTP(current_user.mfa_secret)
    if totp.verify(data['code']):
        current_user.mfa_enabled = True
        await current_user.save()
        return jsonify({'message': 'MFA successfully enabled.'}), 200
    
    return jsonify({'message': 'Invalid code.'}), 400

@app.route('/api/me', methods=['GET'])
@token_required
async def me(current_user):
    return jsonify({'user': {
        'id': str(current_user.id),
        'email': current_user.email,
        'role': current_user.role,
        'name': current_user.name,
        'address': decrypt_pii(current_user.address),
        'phone': decrypt_pii(current_user.phone)
    }}), 200

@app.route('/api/onboarding', methods=['POST'])
@token_required
@rate_limit(10, datetime.timedelta(minutes=1))
async def onboarding(current_user):
    try:
        data = OnboardingSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    current_user.name = data['name']
    current_user.address = encrypt_pii(data['address'])
    current_user.phone = encrypt_pii(data['phone'])
    await current_user.save()
    
    return jsonify({'message': 'Profile updated successfully.'}), 200

@app.route('/api/orders', methods=['GET'])
@token_required
async def orders(current_user):
    orders = await Order.find(Order.user_id == str(current_user.id)).sort('-created_at').to_list()
    return jsonify({'orders': [{'id': str(o.id), 'total': o.total, 'cup_size': o.cup_size, 'collection_time': o.collection_time, 'customer_name': decrypt_pii(o.customer_name), 'status': o.status, 'created_at': o.created_at} for o in orders]}), 200

@app.route('/api/products', methods=['GET'])
async def get_products():
    cached = await redis_client.get('api_products')
    if cached:
        return jsonify(json.loads(cached)), 200
        
    products = await Product.find_all().to_list()
    response_data = {'products': [{'id': str(p.id), 'name': p.name, 'description': p.description, 'price': p.price, 'category': p.category, 'image_url': p.image_url} for p in products]}
    await redis_client.setex('api_products', 300, json.dumps(response_data))
    
    return jsonify(response_data), 200

@app.route('/api/tables', methods=['GET'])
async def get_tables():
    cached = await redis_client.get('api_tables')
    if cached:
        return jsonify(json.loads(cached)), 200
        
    tables = await RestaurantTable.find_all().to_list()
    response_data = {'tables': [{'id': str(t.id), 'table_number': t.table_number, 'status': t.status, 'capacity': t.capacity} for t in tables]}
    await redis_client.setex('api_tables', 300, json.dumps(response_data))
    
    return jsonify(response_data), 200

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
async def admin_orders(current_user):
    orders = await Order.find_all().sort('-created_at').to_list()
    return jsonify({'orders': [{'id': str(o.id), 'total': o.total, 'cup_size': o.cup_size, 'collection_time': o.collection_time, 'customer_name': decrypt_pii(o.customer_name), 'status': o.status, 'created_at': o.created_at, 'payment_method': o.payment_method, 'payment_status': o.payment_status} for o in orders]}), 200

@app.route('/api/admin/tables', methods=['GET'])
@admin_required
async def admin_tables(current_user):
    tables = await RestaurantTable.find_all().to_list()
    return jsonify({'tables': [{'id': str(t.id), 'table_number': t.table_number, 'status': t.status, 'capacity': t.capacity} for t in tables]}), 200

@app.route('/api/admin/employees', methods=['GET'])
@admin_required
async def admin_employees(current_user):
    users = await User.find({"role": {"$in": ["admin", "employee"]}}).to_list()
    employees = []
    for u in users:
        emp = await Employee.find_one(Employee.user_id == str(u.id))
        pos = emp.position if emp else None
        employees.append({'id': str(u.id), 'email': u.email, 'role': u.role, 'position': pos})
    return jsonify({'employees': employees}), 200

@app.route('/api/cart', methods=['GET'])
@token_required
async def get_cart(current_user):
    cart = await Cart.find_one(Cart.user_id == str(current_user.id))
    if cart:
        return jsonify({'cart': json.loads(cart.cart_data)}), 200
    return jsonify({'cart': {}}), 200

@app.route('/api/cart', methods=['POST'])
@token_required
async def save_cart(current_user):
    try:
        data = CartSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    cart_data = data['cart']
    
    cart = await Cart.find_one(Cart.user_id == str(current_user.id))
    if cart:
        cart.cart_data = json.dumps(cart_data)
        await cart.save()
    else:
        await Cart(user_id=str(current_user.id), cart_data=json.dumps(cart_data)).insert()
    
    return jsonify({'message': 'Cart saved successfully'}), 200

@app.route('/api/blog', methods=['GET'])
async def get_blog_posts():
    posts = await BlogPost.all().order_by('-created_at').prefetch_related('author')
    return jsonify({'posts': [{
        'id': str(p.id),
        'title': p.title,
        'content': p.content,
        'image_url': p.image_url,
        'created_at': p.created_at.isoformat(),
        'author_name': p.author.name or p.author.email
    } for p in posts]}), 200

@app.route('/api/blog', methods=['POST'])
@admin_required
async def create_blog_post(current_user):
    data = await request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    
    if not title or not content:
        return jsonify({'message': 'Title and content are required.'}), 400
        
    post = BlogPost(title=title, content=content, image_url=image_url, author_id=str(current_user.id))
    await post.insert()
    
    await AuditLog(
        action="CREATE_BLOG_POST",
        user_id=str(current_user.id),
        target_id=str(post.id),
        details=json.dumps({"title": title})
    ).insert()
    
    app.logger.info(f"Blog post {str(post.id)} created by admin {str(current_user.id)}")
    
    return jsonify({'message': 'Blog post created successfully.'}), 201

@app.route('/api/blog/<string:post_id>', methods=['DELETE'])
@admin_required
async def delete_blog_post(current_user, post_id):
    post = await BlogPost.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
        
    await post.delete()
    
    await AuditLog(
        action="DELETE_BLOG_POST",
        user_id=str(current_user.id),
        target_id=post_id
    ).insert()
    
    app.logger.info(f"Blog post {post_id} deleted by admin {current_user.id}")
    return jsonify({'message': 'Post deleted successfully.'}), 200

@app.route('/api/newsletter', methods=['POST'])
async def subscribe_newsletter():
    try:
        data = NewsletterSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    email = data['email']
    if await NewsletterSubscriber.find_one(NewsletterSubscriber.email == email):
        return jsonify({'message': 'Already subscribed.'}), 400
        
    await NewsletterSubscriber(email=email).insert()
    
    # Enqueue background task to send welcome email
    if arq_pool:
        await arq_pool.enqueue_job('send_newsletter_email', email)
        
    return jsonify({'message': 'Subscribed successfully.'}), 201

@app.route('/api/checkout', methods=['POST'])
@token_required
@rate_limit(5, datetime.timedelta(minutes=1))
async def checkout(current_user):
    try:
        data = CheckoutSchema().load(await request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    customer_name = data['customer_name']
    phone = data['phone']
    collection_time = data['collection_time']
    cup_size = data['cup_size']

    saved_cart = await Cart.find_one(Cart.user_id == str(current_user.id))
    cart = json.loads(saved_cart.cart_data) if saved_cart else {}
    if not isinstance(cart, dict) or not cart:
        return jsonify({'message': 'Your order is empty or invalid.'}), 400
        
    try:
        total = sum(int(item.get('price', 0)) * int(item.get('quantity', 0)) for item in cart.values() if isinstance(item, dict))
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid items in cart.'}), 400
        
    if total <= 0:
        return jsonify({'message': 'Your order could not be priced.'}), 400
        
    payment_method = data['payment_method']
    table_id = data['table_id']
    
    payment_response = {}
    if payment_method == 'stripe':
        try:
            intent = stripe.PaymentIntent.create(
                amount=total * 100,
                currency='inr',
                metadata={'customer': customer_name}
            )
            payment_response = {'client_secret': intent.client_secret, 'provider': 'stripe'}
        except Exception as e:
            app.logger.error(f"Stripe error: {type(e).__name__} occurred during payment processing.")
            return jsonify({'message': 'Payment processing failed.'}), 400
    elif payment_method == 'razorpay':
        try:
            order = razorpay_client.order.create({
                'amount': total * 100,
                'currency': 'INR',
                'receipt': 'receipt_' + customer_name[:5]
            })
            payment_response = {'order_id': order['id'], 'provider': 'razorpay'}
        except Exception as e:
            app.logger.error(f"Razorpay error: {type(e).__name__} occurred during payment processing.")
            return jsonify({'message': 'Payment processing failed.'}), 400
    else:
        payment_response = {'provider': 'mock', 'status': 'success'}

    new_order = Order(
        user_id=str(current_user.id),
        items=json.dumps(cart),
        total=total,
        cup_size=cup_size,
        collection_time=collection_time,
        customer_name=encrypt_pii(customer_name),
        phone=encrypt_pii(phone),
        created_at=datetime.datetime.utcnow().isoformat(timespec='seconds'),
        table_id=str(table_id) if table_id else None,
        payment_method=payment_method,
        payment_status='pending'
    )
    await new_order.insert()
    
    if saved_cart:
        await saved_cart.delete()
        
    app.logger.info(f"Order {str(new_order.id)} placed by user {str(current_user.id)}")
    
    response_data = {'message': 'Order confirmed. Please proceed to payment.', 'order_id': str(new_order.id)}
    response_data.update(payment_response)
    return jsonify(response_data), 201

@app.route('/api/<path:path>', methods=['OPTIONS'])
async def api_options(path):
    return jsonify({}), 200

@app.route('/')
async def index():
    return await send_from_directory(app.static_folder, 'landing.html')

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}

@app.route('/<path:path>')
async def serve_static(path):
    ext = os.path.splitext(path)[1].lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        return await send_from_directory(app.static_folder, '404.html'), 404
        
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return await send_from_directory(app.static_folder, path)
    return await send_from_directory(app.static_folder, '404.html'), 404

@app.errorhandler(404)
async def page_not_found(e):
    return await send_from_directory(app.static_folder, '404.html'), 404

@app.after_request
async def add_security_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        parsed_origin = urlparse(origin)
        if parsed_origin.netloc == request.host:
            response.headers['Access-Control-Allow-Origin'] = origin
            
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; connect-src 'self';"
    
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        
    return response

if __name__ == '__main__':
    import hypercorn.asyncio
    import hypercorn.config
    import asyncio
    
    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:5000"]
    asyncio.run(hypercorn.asyncio.serve(app, config))
