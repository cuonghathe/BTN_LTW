from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f'<Customer {self.id}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return f'<Product {self.product_name}>'


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(50), nullable=False)
    ingredient_picture = db.Column(db.String(1000), nullable=True)

    carts = db.relationship('Cart', backref=db.backref('ingredient', lazy=True))
    orders = db.relationship('Order', backref=db.backref('ingredient', lazy=True))

    def __str__(self):
        return f'<Ingredient {self.name} - {self.quantity} {self.unit}>'


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.String(50), nullable=False)
    serving_size = db.Column(db.Integer, nullable=False)
    recipe_picture = db.Column(db.String(1000), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True)

    def __str__(self):
        return f'<Recipe {self.name}>'


class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    ingredient = db.relationship('Ingredient', backref=db.backref('recipe_ingredients', lazy=True))

    def __str__(self):
        return f'<RecipeIngredient {self.ingredient.name} for {self.recipe.name}>'


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    ingredient_link = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=True)

    def __str__(self):
        return f'<Cart {self.id}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    ingredient_link = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=True)

    def __str__(self):
        return f'<Order {self.id}>'
