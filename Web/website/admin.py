import os
from flask import send_from_directory, Blueprint, render_template, flash, redirect, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import ShopItemsForm, OrderForm, IngredientForm, RecipeForm
from .models import Product, Order, Customer, Ingredient, RecipeIngredient, Recipe
from . import db

admin = Blueprint('admin', __name__)

# Cấu hình thư mục media
MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../media'))
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory(MEDIA_DIR, filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            file = form.product_picture.data
            
            file_name = secure_filename(file.filename)
            file_path = os.path.join(MEDIA_DIR, file_name)
            file.save(file_path)
            
            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=f'media/{file_name}'
            )
            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully')
                return redirect('/add-shop-items')
            except Exception as e:
                flash('Product Not Added!!')
        return render_template('add_shop_items.html', form=form)
    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)
        
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            file = form.product_picture.data
            
            if file:
                file_name = secure_filename(file.filename)
                file_path = os.path.join(MEDIA_DIR, file_name)
                file.save(file_path)
                item_to_update.product_picture = f'media/{file_name}'
            
            item_to_update.product_name = product_name
            item_to_update.current_price = current_price
            item_to_update.previous_price = previous_price
            item_to_update.in_stock = in_stock
            item_to_update.flash_sale = flash_sale
            
            try:
                db.session.commit()
                flash(f'{product_name} updated Successfully')
                return redirect('/shop-items')
            except Exception as e:
                flash('Item Not Updated!!!')
        return render_template('update_item.html', form=form)
    return render_template('404.html')


@admin.route('/add-ingredient', methods=['GET', 'POST'])
@login_required
def add_ingredient():
    if current_user.id == 1:
        form = IngredientForm()

        if form.validate_on_submit():
            name = form.name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            unit = form.unit.data
            quantity = form.quantity.data
            file = form.ingredient_picture.data

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            new_ingredient = Ingredient(
                name=name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                unit=unit,
                quantity=quantity,
                ingredient_picture=file_path
            )

            try:
                db.session.add(new_ingredient)
                db.session.commit()
                flash(f'Ingredient {name} added successfully')
                return redirect('/add-ingredient')
            except Exception as e:
                print(e)
                flash('Ingredient not added!')

        return render_template('add_ingredient.html', form=form)
    return render_template('404.html')


@admin.route('/add-recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if current_user.id == 1:
        form = RecipeForm()
        ingredients = Ingredient.query.all() 
        if form.validate_on_submit():
            name = form.name.data
            description = form.description.data
            instructions = form.instructions.data
            cooking_time = form.cooking_time.data
            serving_size = form.serving_size.data
            file = form.recipe_picture.data

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            new_recipe = Recipe(
                name=name,
                description=description,
                instructions=instructions,
                cooking_time=cooking_time,
                serving_size=serving_size,
                recipe_picture=file_path
            )

            try:
                db.session.add(new_recipe)
                db.session.commit()

                for ingredient_id, quantity, unit in zip(request.form.getlist('ingredient_id'),
                                                        request.form.getlist('quantity'),
                                                        request.form.getlist('unit')):
                    ingredient = Ingredient.query.get(int(ingredient_id))
                    if ingredient:
                        recipe_ingredient = RecipeIngredient(
                            recipe_id=new_recipe.id,
                            ingredient_id=ingredient.id,
                            quantity=float(quantity),
                            unit=unit
                        )
                        db.session.add(recipe_ingredient)

                db.session.commit()
                flash(f'Recipe {name} added successfully')
                return redirect('/add-recipe')

            except Exception as e:
                print(e)
                flash('Recipe not added!')

        return render_template('add_recipe.html', form=form, ingredients=ingredients)
    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')









