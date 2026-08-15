import os
import datetime
import time
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import json
import html
import stripe
import razorpay

from models import db, User, Cart, Order, Product, RestaurantTable, Employee

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

app = Flask(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend')))
app.config['SECRET_KEY'] = load_secret_key()

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    db_path = '/tmp/database.db' if os.environ.get('VERCEL') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def init_db():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            products = [
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
            ]
            db.session.bulk_save_objects(products)
            
        if RestaurantTable.query.count() == 0:
            tables = [RestaurantTable(table_number=str(i), status='available', capacity=4) for i in range(1, 11)]
            db.session.bulk_save_objects(tables)
            
        db.session.commit()

init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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
            user = User.query.get(data['user_id'])
            if not user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin privileges required!'}), 403
        return f(current_user, *args, **kwargs)
    return token_required(decorated)

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    if not email or '@' not in email or len(password) < 8:
        return jsonify({'message': 'Enter a valid email and a password of at least 8 characters.'}), 400
        
    hashed_password = generate_password_hash(password)
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409
        
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    token = jwt.encode({'user_id': new_user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'], algorithm='HS256')
    resp = make_response(jsonify({'message': 'Welcome to Boojee Cafe.', 'user': {'email': email, 'role': 'customer'}}))
    resp.set_cookie('boojee_token', token, httponly=True, secure=True, samesite='Strict', max_age=7*24*60*60)
    return resp, 201

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    resp = make_response(jsonify({'user': {'email': user.email, 'role': user.role}}))
    resp.set_cookie('boojee_token', token, httponly=True, secure=True, samesite='Strict', max_age=7*24*60*60)
    return resp, 200

@app.route('/api/me', methods=['GET'])
@token_required
def me(current_user):
    return jsonify({'user': {
        'id': current_user.id,
        'email': current_user.email,
        'role': current_user.role,
        'name': current_user.name,
        'address': current_user.address,
        'phone': current_user.phone
    }}), 200

@app.route('/api/onboarding', methods=['POST'])
@token_required
def onboarding(current_user):
    data = request.get_json(silent=True) or {}
    name = html.escape((data.get('name') or '').strip())
    address = html.escape((data.get('address') or '').strip())
    phone = html.escape((data.get('phone') or '').strip())
    
    if not name or not address or not phone:
        return jsonify({'message': 'Please provide all required fields.'}), 400
        
    current_user.name = name
    current_user.address = address
    current_user.phone = phone
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully.'}), 200

@app.route('/api/orders', methods=['GET'])
@token_required
def orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return jsonify({'orders': [{'id': o.id, 'total': o.total, 'cup_size': o.cup_size, 'collection_time': o.collection_time, 'customer_name': o.customer_name, 'status': o.status, 'created_at': o.created_at} for o in orders]}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify({'products': [{'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': p.category, 'image_url': p.image_url} for p in products]}), 200

@app.route('/api/tables', methods=['GET'])
def get_tables():
    tables = RestaurantTable.query.all()
    return jsonify({'tables': [{'id': t.id, 'table_number': t.table_number, 'status': t.status, 'capacity': t.capacity} for t in tables]}), 200

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def admin_orders(current_user):
    orders = Order.query.order_by(Order.id.desc()).all()
    return jsonify({'orders': [{'id': o.id, 'total': o.total, 'cup_size': o.cup_size, 'collection_time': o.collection_time, 'customer_name': o.customer_name, 'status': o.status, 'created_at': o.created_at, 'payment_method': o.payment_method, 'payment_status': o.payment_status} for o in orders]}), 200

@app.route('/api/admin/tables', methods=['GET'])
@admin_required
def admin_tables(current_user):
    tables = RestaurantTable.query.all()
    return jsonify({'tables': [{'id': t.id, 'table_number': t.table_number, 'status': t.status, 'capacity': t.capacity} for t in tables]}), 200

@app.route('/api/admin/employees', methods=['GET'])
@admin_required
def admin_employees(current_user):
    results = db.session.query(User.id, User.email, User.role, Employee.position).outerjoin(Employee, User.id == Employee.user_id).filter(User.role.in_(['admin', 'employee'])).all()
    return jsonify({'employees': [{'id': r.id, 'email': r.email, 'role': r.role, 'position': r.position} for r in results]}), 200

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        return jsonify({'cart': json.loads(cart.cart_data)}), 200
    return jsonify({'cart': {}}), 200

@app.route('/api/cart', methods=['POST'])
@token_required
def save_cart(current_user):
    data = request.get_json()
    cart_data = data.get('cart', {})
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        cart.cart_data = json.dumps(cart_data)
    else:
        cart = Cart(user_id=current_user.id, cart_data=json.dumps(cart_data))
        db.session.add(cart)
    db.session.commit()
    
    return jsonify({'message': 'Cart saved successfully'}), 200

from models import BlogPost, NewsletterSubscriber

@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify({'posts': [{
        'id': p.id,
        'title': p.title,
        'content': p.content,
        'image_url': p.image_url,
        'created_at': p.created_at.isoformat(),
        'author_name': p.author.name or p.author.email
    } for p in posts]}), 200

@app.route('/api/blog', methods=['POST'])
@admin_required
def create_blog_post(current_user):
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    
    if not title or not content:
        return jsonify({'message': 'Title and content are required.'}), 400
        
    post = BlogPost(title=title, content=content, image_url=image_url, author_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'message': 'Blog post created successfully.'}), 201

@app.route('/api/blog/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_blog_post(current_user, post_id):
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
        
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully.'}), 200

@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({'message': 'Please enter a valid email address.'}), 400
        
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({'message': 'You are already subscribed!'}), 200
        
    sub = NewsletterSubscriber(email=email)
    db.session.add(sub)
    db.session.commit()
    
    return jsonify({'message': 'Successfully subscribed!'}), 201

@app.route('/api/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    data = request.get_json(silent=True) or {}
    customer_name = html.escape((data.get('customer_name') or '').strip())
    phone = html.escape((data.get('phone') or '').strip())
    collection_time = html.escape((data.get('collection_time') or '').strip())
    cup_size = (data.get('cup_size') or 'Regular').strip()
    if not customer_name or not phone or not collection_time:
        return jsonify({'message': 'Please complete your collection details.'}), 400
    if cup_size not in {'Small', 'Regular', 'Large'}:
        return jsonify({'message': 'Please choose a valid cup size.'}), 400

    saved_cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart = json.loads(saved_cart.cart_data) if saved_cart else {}
    if not cart:
        return jsonify({'message': 'Your order is empty.'}), 400
    total = sum(int(item.get('price', 0)) * int(item.get('quantity', 0)) for item in cart.values())
    if total <= 0:
        return jsonify({'message': 'Your order could not be priced.'}), 400
        
    payment_method = data.get('payment_method', 'mock').strip()
    table_id = data.get('table_id', None)
    
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
            return jsonify({'message': 'Stripe error', 'error': str(e)}), 400
    elif payment_method == 'razorpay':
        try:
            order = razorpay_client.order.create({
                'amount': total * 100,
                'currency': 'INR',
                'receipt': 'receipt_' + customer_name[:5]
            })
            payment_response = {'order_id': order['id'], 'provider': 'razorpay'}
        except Exception as e:
            return jsonify({'message': 'Razorpay error', 'error': str(e)}), 400
    else:
        payment_response = {'provider': 'mock', 'status': 'success'}

    new_order = Order(
        user_id=current_user.id,
        items=json.dumps(cart),
        total=total,
        cup_size=cup_size,
        collection_time=collection_time,
        customer_name=customer_name,
        phone=phone,
        created_at=datetime.datetime.utcnow().isoformat(timespec='seconds'),
        table_id=table_id,
        payment_method=payment_method,
        payment_status='pending'
    )
    db.session.add(new_order)
    
    if saved_cart:
        db.session.delete(saved_cart)
        
    db.session.commit()
    
    response_data = {'message': 'Order confirmed. Please proceed to payment.', 'order_id': new_order.id}
    response_data.update(payment_response)
    return jsonify(response_data), 201

@app.route('/api/<path:path>', methods=['OPTIONS'])
def api_options(path):
    return jsonify({}), 200

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'landing.html')

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}

@app.route('/<path:path>')
def serve_static(path):
    ext = os.path.splitext(path)[1].lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        return send_from_directory(app.static_folder, '404.html'), 404
        
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, '404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory(app.static_folder, '404.html'), 404

@app.after_request
def add_security_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' *; style-src 'self' 'unsafe-inline' https://*; font-src 'self' https://*; script-src 'self' 'unsafe-inline' https://*; connect-src 'self' http://localhost:5000 http://127.0.0.1:5000 https://*;"
    return response

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
