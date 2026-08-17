import re

def rewrite():
    with open('backend/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Imports
    content = content.replace("from tortoise import Tortoise", "from beanie import init_beanie\nfrom motor.motor_asyncio import AsyncIOMotorClient")
    content = content.replace("from tortoise.exceptions import IntegrityError\n", "")
    content = content.replace("from tortoise.transactions import in_transaction\n", "")
    
    # 2. DB Config
    content = re.sub(r'DB_URL = os\.environ\.get\(\'DATABASE_URL\', \'sqlite://database\.db\'\)', 
                     "DB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')", content)
                     
    content = re.sub(r'TORTOISE_ORM = \{[\s\S]*?\}\n', "", content)
    
    # 3. init_db
    init_db_old = """@app.before_serving
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    # Initialize mock data
    if await Product.all().count() == 0:
        await Product.bulk_create(["""
        
    init_db_new = """@app.before_serving
async def init_db():
    client = AsyncIOMotorClient(DB_URL)
    await init_beanie(database=client.boojee, document_models=[User, Cart, Order, Product, RestaurantTable, Employee, RevokedToken, BlogPost, NewsletterSubscriber])
    
    # Initialize mock data
    if await Product.find_all().count() == 0:
        await Product.insert_many(["""
    
    content = content.replace(init_db_old, init_db_new)
    content = content.replace("if await RestaurantTable.all().count() == 0:", "if await RestaurantTable.find_all().count() == 0:")
    content = content.replace("await RestaurantTable.bulk_create([", "await RestaurantTable.insert_many([")
    
    # 4. close_db
    close_db_old = """@app.after_serving
async def close_db():
    await Tortoise.close_connections()"""
    close_db_new = """@app.after_serving
async def close_db():
    pass"""
    content = content.replace(close_db_old, close_db_new)
    
    # 5. token_required
    content = content.replace("if await RevokedToken.filter(jti=data.get('jti')).exists():", "if await RevokedToken.find_one(RevokedToken.jti == data.get('jti')) is not None:")
    content = content.replace("user = await User.get_or_none(id=data['user_id'])", "user = await User.get(data['user_id'])")
    
    # 6. register
    content = content.replace("if await User.filter(email=email).exists():", "if await User.find_one(User.email == email) is not None:")
    content = content.replace("new_user = await User.create(email=email, password=hashed_password)", "new_user = User(email=email, password=hashed_password)\n    await new_user.insert()")
    content = content.replace("'user_id': new_user.id", "'user_id': str(new_user.id)")
    
    # 7. login
    content = content.replace("user = await User.get_or_none(email=email)", "user = await User.find_one(User.email == email)")
    content = content.replace("'user_id': user.id", "'user_id': str(user.id)")
    
    # 8. logout
    content = content.replace("await RevokedToken.create(jti=data['jti'])", "await RevokedToken(jti=data['jti']).insert()")
    
    # 9. me
    content = content.replace("'id': current_user.id", "'id': str(current_user.id)")
    
    # 10. orders
    content = content.replace("orders = await Order.filter(user_id=current_user.id).order_by('-id')", "orders = await Order.find(Order.user_id == str(current_user.id)).sort('-created_at').to_list()")
    content = content.replace("'id': o.id,", "'id': str(o.id),")
    
    # 11. products
    content = content.replace("products = await Product.all()", "products = await Product.find_all().to_list()")
    content = content.replace("'id': p.id,", "'id': str(p.id),")
    
    # 12. tables
    content = content.replace("tables = await RestaurantTable.all()", "tables = await RestaurantTable.find_all().to_list()")
    content = content.replace("'id': t.id,", "'id': str(t.id),")
    
    # 13. admin/orders
    content = content.replace("orders = await Order.all().order_by('-id')", "orders = await Order.find_all().sort('-created_at').to_list()")
    
    # 14. admin/employees
    admin_emp_old = """users = await User.filter(role__in=['admin', 'employee']).prefetch_related('employee_profile')
    employees = []
    for u in users:
        pos = u.employee_profile.position if hasattr(u, 'employee_profile') and u.employee_profile else None
        employees.append({'id': u.id, 'email': u.email, 'role': u.role, 'position': pos})"""
    
    admin_emp_new = """users = await User.find({"role": {"$in": ["admin", "employee"]}}).to_list()
    employees = []
    for u in users:
        emp = await Employee.find_one(Employee.user_id == str(u.id))
        pos = emp.position if emp else None
        employees.append({'id': str(u.id), 'email': u.email, 'role': u.role, 'position': pos})"""
        
    content = content.replace(admin_emp_old, admin_emp_new)
    
    # 15. cart GET
    content = content.replace("cart = await Cart.get_or_none(user_id=current_user.id)", "cart = await Cart.find_one(Cart.user_id == str(current_user.id))")
    
    # 16. cart POST
    content = content.replace("await Cart.create(user_id=current_user.id, cart_data=json.dumps(cart_data))", "await Cart(user_id=str(current_user.id), cart_data=json.dumps(cart_data)).insert()")
    
    # 17. blog GET
    blog_get_old = """posts = await BlogPost.all().order_by('-created_at').prefetch_related('author')
    return jsonify({'posts': [{
        'id': p.id,
        'title': p.title,
        'content': p.content,
        'image_url': p.image_url,
        'created_at': p.created_at.isoformat(),
        'author_name': p.author.name or p.author.email
    } for p in posts]}), 200"""
    
    blog_get_new = """posts = await BlogPost.find_all().sort('-created_at').to_list()
    result = []
    for p in posts:
        author = await User.get(p.author_id)
        author_name = author.name or author.email if author else "Unknown"
        result.append({
            'id': str(p.id),
            'title': p.title,
            'content': p.content,
            'image_url': p.image_url,
            'created_at': p.created_at.isoformat(),
            'author_name': author_name
        })
    return jsonify({'posts': result}), 200"""
    content = content.replace(blog_get_old, blog_get_new)
    
    # 18. blog POST
    content = content.replace("post = await BlogPost.create(title=title, content=content, image_url=image_url, author_id=current_user.id)", "post = BlogPost(title=title, content=content, image_url=image_url, author_id=str(current_user.id))\n    await post.insert()")
    content = content.replace("app.logger.info(f\"Blog post {post.id} created by admin {current_user.id}\")", "app.logger.info(f\"Blog post {str(post.id)} created by admin {str(current_user.id)}\")")
    
    # 19. blog DELETE
    content = content.replace("@app.route('/api/blog/<int:post_id>', methods=['DELETE'])", "@app.route('/api/blog/<string:post_id>', methods=['DELETE'])")
    content = content.replace("post = await BlogPost.get_or_none(id=post_id)", "post = await BlogPost.get(post_id)")
    
    # 20. newsletter
    content = content.replace("existing = await NewsletterSubscriber.get_or_none(email=email)", "existing = await NewsletterSubscriber.find_one(NewsletterSubscriber.email == email)")
    content = content.replace("await NewsletterSubscriber.create(email=email)", "await NewsletterSubscriber(email=email).insert()")
    
    # 21. checkout
    checkout_old = """    async with in_transaction():
        new_order = await Order.create(
            user_id=current_user.id,
            items=json.dumps(cart),
            total=total,
            cup_size=cup_size,
            collection_time=collection_time,
            customer_name=encrypt_pii(customer_name),
            phone=encrypt_pii(phone),
            created_at=datetime.datetime.utcnow().isoformat(timespec='seconds'),
            table_id=table_id,
            payment_method=payment_method,
            payment_status='pending'
        )
        
        if saved_cart:
            await saved_cart.delete()
        
    app.logger.info(f"Order {new_order.id} placed by user {current_user.id}")
    
    response_data = {'message': 'Order confirmed. Please proceed to payment.', 'order_id': new_order.id}"""
    
    checkout_new = """    new_order = Order(
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
    
    response_data = {'message': 'Order confirmed. Please proceed to payment.', 'order_id': str(new_order.id)}"""
    
    content = content.replace(checkout_old, checkout_new)
    
    with open('backend/app.py', 'w', encoding='utf-8') as f:
        f.write(content)

rewrite()
