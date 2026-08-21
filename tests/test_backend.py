import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from app import app  # type: ignore
from models import User, RevokedToken, Cart, Order, Product, RestaurantTable, Employee, BlogPost, NewsletterSubscriber, AuditLog, Enquiry  # type: ignore
from werkzeug.security import check_password_hash
import json
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    app.config['TESTING'] = True
    import mongomock
    
    # Mock MongoDB for tests
    mock_client = AsyncMongoMockClient()
    
    original_list_collection_names = mongomock.database.Database.list_collection_names
    
    def patched_list_collection_names(self, *args, **kwargs):
        return original_list_collection_names(self)
        
    mongomock.database.Database.list_collection_names = patched_list_collection_names
    
    await init_beanie(
        database=mock_client.boojee_test, 
        document_models=[User, Cart, Order, Product, RestaurantTable, Employee, RevokedToken, BlogPost, NewsletterSubscriber, AuditLog, Enquiry]
    )
    
    class MockRedis:
        def __init__(self):
            self.data = {}
        async def get(self, key):
            return self.data.get(key)
        async def set(self, key, value, *args, **kwargs):
            self.data[key] = value
        async def setex(self, key, ttl, value):
            self.data[key] = value

    import app as backend_app  # type: ignore
    backend_app.redis_client = MockRedis()
    
    # Quart test client
    client = app.test_client()
    
    yield client

@pytest.mark.asyncio
async def test_register_strict_validation(client):
    # Test weak password rejection (Marshmallow Schema)
    response = await client.post('/api/register', json={
        'email': 'test@example.com',
        'password': 'weak'
    }, headers={'Origin': 'http://localhost'})
    assert response.status_code == 400
    data = await response.get_json()
    assert 'Validation error' in data['message']

@pytest.mark.asyncio
async def test_register_scrypt_hashing(client):
    # Test valid registration
    response = await client.post('/api/register', json={
        'email': 'test@example.com',
        'password': 'StrongPassword123!'
    }, headers={'Origin': 'http://localhost'})
    assert response.status_code == 201
    
    # Verify DB insertion and scrypt format
    user = await User.find_one(User.email == 'test@example.com')
    assert user is not None
    assert user.password.startswith('scrypt:')
    assert check_password_hash(user.password, 'StrongPassword123!')

@pytest.mark.asyncio
async def test_cart_schema_validation(client):
    # Test that malicious cart structures are blocked
    response = await client.post('/api/cart', json={
        'cart': 'this is a string, not a dict'
    }, headers={'Origin': 'http://localhost'})
    # Will be 401 because no token
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_and_logout_blacklisting(client):
    # 1. Register
    await client.post('/api/register', json={
        'email': 'user@example.com',
        'password': 'StrongPassword123!'
    }, headers={'Origin': 'http://localhost'})
    
    # 2. Login
    login_res = await client.post('/api/login', json={
        'email': 'user@example.com',
        'password': 'StrongPassword123!'
    }, headers={'Origin': 'http://localhost'})
    assert login_res.status_code == 200
    
    # Extract token
    token = None
    for cookie_header in login_res.headers.get_all('Set-Cookie'):
        if 'boojee_token=' in cookie_header:
            token = cookie_header.split('boojee_token=')[1].split(';')[0]
            
    assert token is not None
    
    # 3. Access protected route
    me_res = await client.get('/api/me', headers={'Authorization': f'Bearer {token}'})
    assert me_res.status_code == 200
    
    # 4. Logout (Blacklist Token)
    logout_res = await client.post('/api/logout', headers={'Authorization': f'Bearer {token}', 'Origin': 'http://localhost'})
    assert logout_res.status_code == 200
    
    # 5. Access protected route again (Should be denied)
    me_res_blocked = await client.get('/api/me', headers={'Authorization': f'Bearer {token}'})
    assert me_res_blocked.status_code == 401
    data = await me_res_blocked.get_data()
    assert b'Token has been revoked.' in data


@pytest.mark.asyncio
async def test_enquiry_creation(client):
    response = await client.post('/api/enquiries', json={
        'name': 'Harshil',
        'email': 'harshil@example.com',
        'enquiry_type': 'gathering',
        'date': '2026-09-15',
        'message': 'Looking to book a table for a coffee tasting gathering.'
    }, headers={'Origin': 'http://localhost'})
    assert response.status_code == 201
    data = await response.get_json()
    assert data['message'] == 'Enquiry received successfully.'
