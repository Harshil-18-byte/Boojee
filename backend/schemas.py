from marshmallow import Schema, fields, validate, ValidationError

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
            error="Password must be at least 8 characters long and contain a letter, a number, and a special character."
        )
    )

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class OnboardingSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    address = fields.String(required=True, validate=validate.Length(min=5))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))

class CartItemSchema(Schema):
    price = fields.Integer(required=True, strict=True, validate=validate.Range(min=0))
    quantity = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=100))

class CartSchema(Schema):
    cart = fields.Dict(keys=fields.String(), values=fields.Nested(CartItemSchema), required=True)

class CheckoutSchema(Schema):
    customer_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    collection_time = fields.String(required=True, validate=validate.Length(min=1, max=50))
    cup_size = fields.String(load_default='Regular', validate=validate.OneOf(['Small', 'Regular', 'Large']))
    payment_method = fields.String(load_default='mock', validate=validate.OneOf(['mock', 'stripe', 'razorpay']))
    table_id = fields.Integer(load_default=None, allow_none=True)

class NewsletterSchema(Schema):
    email = fields.Email(required=True)
