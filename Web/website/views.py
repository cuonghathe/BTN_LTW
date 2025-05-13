from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order, Ingredient, Recipe
from flask_login import login_required, current_user
from . import db
from intasend import APIService


views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'


@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                        if current_user.is_authenticated else [])
    


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)


@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()

    if not customer_cart:
        flash('Giỏ hàng của bạn đang trống')
        return redirect('/')

    try:
        total = 0
        for item in customer_cart:
            total += item.product.current_price * item.quantity

        # ✅ THAY THẾ ĐOẠN THANH TOÁN BẰNG DỮ LIỆU GIẢ ĐỂ TEST
        create_order_response = {
            'invoice': {'state': 'completed'},
            'id': 'TEST_ORDER_123456'
        }

        for item in customer_cart:
            product = Product.query.get(item.product_link)

            # ✅ Kiểm tra tồn kho
            if item.quantity > product.in_stock:
                flash(f"Sản phẩm '{product.product_name}' không đủ hàng trong kho.")
                return redirect('/cart')

            new_order = Order()
            new_order.quantity = item.quantity
            new_order.price = item.product.current_price
            new_order.status = create_order_response['invoice']['state'].capitalize()
            new_order.payment_id = create_order_response['id']
            new_order.product_link = item.product_link
            new_order.customer_link = item.customer_link

            db.session.add(new_order)

            # Trừ tồn kho
            product.in_stock -= item.quantity

            # Xoá khỏi giỏ hàng
            db.session.delete(item)

        db.session.commit()

        flash('Đặt hàng thành công!')
        return redirect('/orders')

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash('Lỗi xảy ra khi đặt hàng. Vui lòng thử lại.')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                        if current_user.is_authenticated else [])

    return render_template('search.html')

@views.route("/mat-hang")
def mat_hang():
    items = Product.query.all()  # hoặc tên model của bạn
    return render_template("mat_hang.html", items=items)

@views.route("/nguyen-lieu")
def nguyen_lieu():
    ingre = Ingredient.query.all()  # hoặc tên model nguyên liệu của bạn
    return render_template("nguyen_lieu.html", ingre=ingre)

@views.route("/cong-thuc")
def cong_thuc():
    recipes = Recipe.query.all()
    return render_template("cong_thuc.html", recipes=recipes)


@views.route("/chi-tiet-cong-thuc/<int:recipe_id>")
def chi_tiet_cong_thuc(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template("chi_tiet_cong_thuc.html", recipe=recipe)
















