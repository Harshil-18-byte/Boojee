from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False)

class Cart(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'carts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    cart_data = db.Column(db.Text, nullable=False)

class Order(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    cup_size = db.Column(db.String(20), nullable=False, default='Regular')
    collection_time = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    created_at = db.Column(db.String(50), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('restaurant_tables.id'), nullable=True)
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=True)

class Product(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))

class RestaurantTable(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'restaurant_tables'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    capacity = db.Column(db.Integer, nullable=False, default=4)

class Employee(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    position = db.Column(db.String(100))
    user = db.relationship('User', backref='employee_profile')

class BlogPost(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User')

class NewsletterSubscriber(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = 'newsletter_subscribers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

class RevokedToken(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

