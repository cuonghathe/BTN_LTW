from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Khởi tạo SQLAlchemy
db = SQLAlchemy()
DB_NAME = 'database.sqlite3'


def create_database(app):
    """Tạo cơ sở dữ liệu nếu chưa tồn tại."""
    with app.app_context():
        if not os.path.exists(DB_NAME):
            db.create_all()
            print('Database Created')


def create_app():
    """Khởi tạo ứng dụng Flask."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hbnwdvbn ajnbsjn ahe'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Xử lý lỗi 404
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    # Cấu hình Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        from .models import Customer
        return Customer.query.get(int(id))

    # Import và đăng ký các blueprint
    from .views import views
    from .auth import auth
    from .admin import admin
    from .recipe import recipe  # Import recipe blueprint
    from .models import Customer, Cart, Product, Order, Recipe  # Import các model

    app.register_blueprint(views, url_prefix='/')  # localhost:5000/
    app.register_blueprint(auth, url_prefix='/auth')  # localhost:5000/auth/
    app.register_blueprint(admin, url_prefix='/admin')  # localhost:5000/admin/
    app.register_blueprint(recipe, url_prefix='/recipe')  # localhost:5000/recipe/

    # Tạo cơ sở dữ liệu nếu chưa tồn tại
    create_database(app)

    return app