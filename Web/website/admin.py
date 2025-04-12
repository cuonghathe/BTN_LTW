import os
from flask import send_from_directory, Blueprint, render_template, flash, redirect, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import ShopItemsForm, OrderForm, IngredientForm, RecipeForm, RecipeIngredientForm
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

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('Xoá thành công')
            return redirect('/shop-items')
        except Exception as e:
            print('Lỗi', e)
            flash('Lỗi!!')
        return redirect('/shop-items')

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
            flash_sale = form.flash_sale.data  # Added Flash Sale
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
                flash_sale=flash_sale,  # Added Flash Sale
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

@admin.route('/shop-ingredient', methods=['GET', 'POST'])
@login_required
def shop_ingredient():
    if current_user.id == 1:
        ingre = Ingredient.query.order_by(Ingredient.date_added).all()
        return render_template('shop_ingredient.html', ingre=ingre)
    return render_template('404.html')

@admin.route('/update-ingredient/<int:ingre_id>', methods=['GET', 'POST'])
@login_required
def update_ingredient(ingre_id):
    if current_user.id == 1:
        # Fetch the ingredient to be updated
        ingre_to_update = Ingredient.query.get_or_404(ingre_id)

        # Initialize the form
        form = IngredientForm()

        # On GET request: Pre-fill the form with existing ingredient info
        if request.method == 'GET':
            # Populate the form fields with the current ingredient data
            form.name.data = ingre_to_update.name
            form.current_price.data = ingre_to_update.current_price
            form.previous_price.data = ingre_to_update.previous_price
            form.in_stock.data = ingre_to_update.in_stock
            form.unit.data = ingre_to_update.unit
            form.quantity.data = ingre_to_update.quantity
            form.flash_sale.data = ingre_to_update.flash_sale

        # On POST request: Process the form submission
        elif form.validate_on_submit():
            ingre_to_update.name = form.name.data
            ingre_to_update.current_price = form.current_price.data
            ingre_to_update.previous_price = form.previous_price.data
            ingre_to_update.in_stock = form.in_stock.data
            ingre_to_update.unit = form.unit.data
            ingre_to_update.quantity = form.quantity.data
            ingre_to_update.flash_sale = form.flash_sale.data

            # Check if a new image has been uploaded
            file = form.ingredient_picture.data
            if file:
                file_name = secure_filename(file.filename)
                file_path = os.path.join(MEDIA_DIR, file_name)
                file.save(file_path)
                ingre_to_update.ingredient_picture = f'media/{file_name}'

            try:
                # Commit the changes to the database
                db.session.commit()
                flash(f'{form.name.data} updated successfully!', 'success')
                return redirect('/shop-ingredient')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating ingredient: {str(e)}', 'danger')

        return render_template('update_ingredient.html', form=form, ingre=ingre_to_update)

    return render_template('404.html')


@admin.route('/delete-ingredient/<int:ingre_id>', methods=['GET', 'POST'])
@login_required
def delete_ingredient(ingre_id):
    if current_user.id == 1:
        ingredient_to_delete = Ingredient.query.get_or_404(ingre_id)
        try:
            db.session.delete(ingredient_to_delete)
            db.session.commit()
            flash(f'Ingredient {ingredient_to_delete.name} deleted successfully!', 'success')
            return redirect('/shop-ingredient')
        except Exception as e:
            flash(f'Error deleting ingredient: {str(e)}', 'danger')
            return redirect('/shop-ingredient')
    return render_template('404.html')



@admin.route('/add-recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if current_user.id != 1:
        return render_template('404.html')

    form = RecipeForm()

    if request.method == 'GET':
        for _ in range(3):
            form.ingredients.append_entry()

    # Set ingredient choices
    ingredients = [(str(ing.id), ing.name) for ing in Ingredient.query.all()]
    for entry in form.ingredients.entries:
        entry.form.ingredient.choices = ingredients

    if form.validate_on_submit():
        try:
            file = form.recipe_picture.data
            picture_path = None
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(MEDIA_DIR, filename)
                file.save(filepath)
                picture_path = f'media/{filename}'

            new_recipe = Recipe(
                name=form.name.data,
                description=form.description.data,
                instructions=form.instructions.data,
                cooking_time=form.cooking_time.data,
                serving_size=form.serving_size.data,
                recipe_picture=picture_path
            )
            db.session.add(new_recipe)
            db.session.flush()  # To get ID

            for entry in form.ingredients.entries:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    ingredient_id=int(entry.form.ingredient.data),
                    quantity=entry.form.quantity.data,
                    unit=entry.form.unit.data
                )
                db.session.add(recipe_ingredient)

            db.session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('admin.shop_recipe'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding recipe: {e}', 'danger')

    else:
        print("🔴 Form.errors:", form.errors)
        for i, entry in enumerate(form.ingredients.entries):
            print(f"🧪 Ingredient #{i} errors:", entry.form.errors)
        flash('Thêm công thức')

    return render_template('add_recipe.html', form=form)



@admin.route('/shop-recipe', methods=['GET', 'POST'])
@login_required
def shop_recipe():
    if current_user.id == 1:
        recipes = Recipe.query.order_by(Recipe.date_added).all()
        return render_template('shop_recipe.html', recipes=recipes)
    return render_template('404.html')


@admin.route('/update-recipe/<int:recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = RecipeForm()

    # On GET: preload data into the form
    if request.method == 'GET':
        form.name.data = recipe.name
        form.description.data = recipe.description
        form.instructions.data = recipe.instructions
        form.cooking_time.data = recipe.cooking_time
        form.serving_size.data = recipe.serving_size

        # Clear default entries
        form.ingredients.entries = []

        # Get all ingredients for the dropdown
        all_ingredients = Ingredient.query.all()
        ingredient_choices = [(str(i.id), i.name) for i in all_ingredients]

        # Add each ingredient from recipe into the form
        for ri in recipe.ingredients:
            ingredient_form = RecipeIngredientForm()
            ingredient_form.ingredient.choices = ingredient_choices
            ingredient_form.ingredient.data = str(ri.ingredient_id)
            ingredient_form.quantity.data = ri.quantity
            ingredient_form.unit.data = ri.unit
            form.ingredients.append_entry(ingredient_form)

    # On POST: update recipe
    elif form.validate_on_submit():
        recipe.name = form.name.data
        recipe.description = form.description.data
        recipe.instructions = form.instructions.data
        recipe.cooking_time = form.cooking_time.data
        recipe.serving_size = form.serving_size.data

        # Remove old ingredients
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        for ingredient_form in form.ingredients:
            new_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=int(ingredient_form.ingredient.data),
                quantity=ingredient_form.quantity.data,
                unit=ingredient_form.unit.data
            )
            db.session.add(new_ingredient)

        db.session.commit()
        flash('Cập nhật công thức thành công!', 'success')
        return redirect('/shop-recipe')

    # Set ingredient choices on POST too (important!)
    for entry in form.ingredients.entries:
        entry.ingredient.choices = [(str(i.id), i.name) for i in Ingredient.query.all()]

    return render_template('update_recipe.html', form=form, recipe=recipe)



@admin.route('/delete-recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    if current_user.id == 1:
        recipe_to_delete = Recipe.query.get_or_404(recipe_id)
        try:
            # Delete associated ingredients in RecipeIngredient first
            RecipeIngredient.query.filter_by(recipe_id=recipe_to_delete.id).delete()

            db.session.delete(recipe_to_delete)
            db.session.commit()
            flash(f'Công thức "{recipe_to_delete.name}" đã được xóa thành công!', 'success')
            return redirect('/shop-recipe')
        except Exception as e:
            flash(f'Có lỗi khi xóa công thức: {str(e)}', 'danger')
            return redirect('/shop-recipe')
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









