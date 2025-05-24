from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Создаем Blueprint для аутентификации
auth_bp = Blueprint('auth', __name__)

# Класс пользователя для Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Функция для загрузки пользователя
def load_user(user_id):
    # В нашем случае у нас только один пользователь - администратор
    if user_id == '1':
        # Получаем пароль из настроек
        database = current_app.config['DATABASE']
        password_hash = database.get_setting('admin_password_hash')
        if not password_hash:
            # Если пароль не установлен, используем значение по умолчанию из конфига
            from bot.config import ADMIN_PASSWORD
            password_hash = generate_password_hash(ADMIN_PASSWORD)
            database.set_setting('admin_password_hash', password_hash)
        
        return User(id='1', username='admin', password_hash=password_hash)
    return None

# Маршрут для входа
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Получаем пользователя
        user = load_user('1')
        
        # Проверяем пароль
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('channels.index'))
        else:
            flash('Неверный пароль. Попробуйте снова.')
    
    return render_template('login.html')

# Маршрут для выхода
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Маршрут для смены пароля
@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверяем текущий пароль
        if not current_user.check_password(current_password):
            flash('Текущий пароль неверен.')
            return redirect(url_for('auth.change_password'))
        
        # Проверяем совпадение новых паролей
        if new_password != confirm_password:
            flash('Новые пароли не совпадают.')
            return redirect(url_for('auth.change_password'))
        
        # Обновляем пароль
        database = current_app.config['DATABASE']
        password_hash = generate_password_hash(new_password)
        database.set_setting('admin_password_hash', password_hash)
        
        flash('Пароль успешно изменен.')
        return redirect(url_for('settings.index'))
    
    return render_template('change_password.html')
