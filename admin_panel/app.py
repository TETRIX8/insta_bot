from flask import Flask
from flask_login import LoginManager
import os
from datetime import timedelta

def create_app(database):
    """Создание и настройка Flask приложения"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['DATABASE'] = database
    
    # Настройка Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Импорт и регистрация маршрутов
    from admin_panel.routes import channels, comments, settings
    from admin_panel.auth import auth_bp, User, load_user
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(channels.channels_bp)
    app.register_blueprint(comments.comments_bp)
    app.register_blueprint(settings.settings_bp)
    
    # Настройка загрузчика пользователей
    login_manager.user_loader(load_user)
    
    return app
