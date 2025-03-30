from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, \
    SelectField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField
from .models import Ingredient


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    description = TextAreaField('Description')
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])
    update = SubmitField('Update Status')


class IngredientForm(FlaskForm):
    name = StringField('Ingredient Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    unit = StringField('Unit of Measurement', validators=[DataRequired()])
    ingredient_picture = FileField('Ingredient Picture')

    add_ingredient = SubmitField('Add Ingredient')
    update_ingredient = SubmitField('Update')


class RecipeIngredientForm(FlaskForm):
    ingredient = SelectField('Ingredient', choices=[], validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.1)])
    unit = StringField('Unit of Measurement', validators=[DataRequired()])


class RecipeForm(FlaskForm):
    name = StringField('Recipe Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    cooking_time = StringField('Cooking Time', validators=[DataRequired()])
    serving_size = IntegerField('Serving Size', validators=[DataRequired(), NumberRange(min=1)])
    recipe_picture = FileField('Recipe Picture')

    ingredients = FieldList(FormField(RecipeIngredientForm), min_entries=1)

    add_recipe = SubmitField('Add Recipe')
    update_recipe = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients.entries[0].form.ingredient.choices = [(str(ingredient.id), ingredient.name) for ingredient in
                                                                Ingredient.query.all()]
