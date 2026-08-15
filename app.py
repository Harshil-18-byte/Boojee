import os
import sqlite3
import datetime
import time
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import json
import html

# In-memory rate limiting store (IP -> list of timestamps)
rate_limits = {}

def is_rate_limited(ip, limit=5, window=60):
    now = time.time()
    if ip not in rate_limits:
        rate_limits[ip] = []
    # Clean up old timestamps
    rate_limits[ip] = [t for t in rate_limits[ip] if now - t < window]
    if len(rate_limits[ip]) >= limit:
        return True
    rate_limits[ip].append(now)
    return False

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

app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = load_secret_key()
if os.environ.get('VERCEL'):
    DATABASE = '/tmp/database.db'
else:
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            user_id INTEGER PRIMARY KEY,
            cart_data TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            cup_size TEXT NOT NULL DEFAULT 'Regular',
            collection_time TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'confirmed',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    order_columns = [row['name'] for row in conn.execute('PRAGMA table_info(orders)').fetchall()]
    if 'cup_size' not in order_columns:
        c.execute("ALTER TABLE orders ADD COLUMN cup_size TEXT NOT NULL DEFAULT 'Regular'")
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],)).fetchone()
            conn.close()
            if not user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(user, *args, **kwargs)
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({'message': 'Too many attempts. Please try again later.'}), 429
        
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    if not email or '@' not in email or len(password) < 8:
        return jsonify({'message': 'Enter a valid email and a password of at least 8 characters.'}), 400
        
    hashed_password = generate_password_hash(password)
    
    conn = get_db()
    try:
        cursor = conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'User already exists'}), 409
    
    user_id = cursor.lastrowid
    conn.close()
    token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'message': 'Welcome to Boojee Cafe.', 'token': token, 'user': {'email': email}}), 201

@app.route('/api/login', methods=['POST'])
def login():
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({'message': 'Too many attempts. Please try again later.'}), 429
        
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({'token': token, 'user': {'email': user['email']}}), 200

@app.route('/api/me', methods=['GET'])
@token_required
def me(current_user):
    return jsonify({'user': {'id': current_user['id'], 'email': current_user['email']}}), 200

@app.route('/api/orders', methods=['GET'])
@token_required
def orders(current_user):
    conn = get_db()
    rows = conn.execute('SELECT id, total, cup_size, collection_time, customer_name, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC', (current_user['id'],)).fetchall()
    conn.close()
    return jsonify({'orders': [dict(row) for row in rows]}), 200

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    conn = get_db()
    cart = conn.execute('SELECT cart_data FROM carts WHERE user_id = ?', (current_user['id'],)).fetchone()
    conn.close()
    
    if cart:
        return jsonify({'cart': json.loads(cart['cart_data'])}), 200
    return jsonify({'cart': {}}), 200

@app.route('/api/cart', methods=['POST'])
@token_required
def save_cart(current_user):
    data = request.get_json()
    cart_data = data.get('cart', {})
    
    conn = get_db()
    conn.execute('''
        INSERT INTO carts (user_id, cart_data) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET cart_data = excluded.cart_data
    ''', (current_user['id'], json.dumps(cart_data)))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Cart saved successfully'}), 200

@app.route('/api/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    data = request.get_json(silent=True) or {}
    # Strict sanitization of user input to prevent Stored XSS
    customer_name = html.escape((data.get('customer_name') or '').strip())
    phone = html.escape((data.get('phone') or '').strip())
    collection_time = html.escape((data.get('collection_time') or '').strip())
    cup_size = (data.get('cup_size') or 'Regular').strip()
    if not customer_name or not phone or not collection_time:
        return jsonify({'message': 'Please complete your collection details.'}), 400
    if cup_size not in {'Small', 'Regular', 'Large'}:
        return jsonify({'message': 'Please choose a valid cup size.'}), 400

    conn = get_db()
    saved_cart = conn.execute('SELECT cart_data FROM carts WHERE user_id = ?', (current_user['id'],)).fetchone()
    cart = json.loads(saved_cart['cart_data']) if saved_cart else {}
    if not cart:
        conn.close()
        return jsonify({'message': 'Your order is empty.'}), 400
    total = sum(int(item.get('price', 0)) * int(item.get('quantity', 0)) for item in cart.values())
    if total <= 0:
        conn.close()
        return jsonify({'message': 'Your order could not be priced.'}), 400
    cursor = conn.execute(
        '''INSERT INTO orders (user_id, items, total, cup_size, collection_time, customer_name, phone, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (current_user['id'], json.dumps(cart), total, cup_size, collection_time, customer_name, phone,
         datetime.datetime.utcnow().isoformat(timespec='seconds'))
    )
    conn.execute('DELETE FROM carts WHERE user_id = ?', (current_user['id'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Order confirmed. We will have it ready for collection.', 'order_id': cursor.lastrowid}), 201

@app.route('/api/<path:path>', methods=['OPTIONS'])
def api_options(path):
    return jsonify({}), 200

# Serve static files from the root directory
@app.route('/')
def index():
    return send_from_directory('.', 'landing.html')

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}

@app.route('/<path:path>')
def serve_static(path):
    ext = os.path.splitext(path)[1].lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        return send_from_directory('.', '404.html'), 404
        
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', '404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('.', '404.html'), 404

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
