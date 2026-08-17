from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional, List, Dict, Annotated
from datetime import datetime
from bson import ObjectId

class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str
    role: str = "customer"
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False

    class Settings:
        name = "users"

class Cart(Document):
    user_id: str
    cart_data: str
    
    class Settings:
        name = "carts"

class RestaurantTable(Document):
    table_number: Annotated[str, Indexed(unique=True)]
    status: str = "available"
    capacity: int = 4

    class Settings:
        name = "restaurant_tables"

class Employee(Document):
    user_id: str
    position: Optional[str] = None

    class Settings:
        name = "employees"

class Order(Document):
    user_id: str
    items: str
    total: int
    cup_size: str = "Regular"
    collection_time: str
    customer_name: str
    phone: str
    status: str = "confirmed"
    created_at: str
    table_id: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    payment_status: str = "pending"
    payment_method: Optional[str] = None

    class Settings:
        name = "orders"

class Product(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: Optional[str] = None
    price: int
    category: str
    image_url: Optional[str] = None

    class Settings:
        name = "products"

class BlogPost(Document):
    title: str
    content: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: str

    class Settings:
        name = "blog_posts"

class NewsletterSubscriber(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "newsletter_subscribers"

class AuditLog(Document):
    action: str
    user_id: Optional[str] = None
    target_id: Optional[str] = None
    details: Optional[str] = None # JSON string if needed
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "audit_logs"

class RevokedToken(Document):
    jti: Annotated[str, Indexed(unique=True)]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "revoked_tokens"
