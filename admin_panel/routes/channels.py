from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
import asyncio

# Создаем Blueprint для управления каналами
channels_bp = Blueprint('channels', __name__, url_prefix='/channels')

@channels_bp.route('/')
@login_required
def index():
    """Страница со списком каналов"""
    database = current_app.config['DATABASE']
    channels = database.get_channels(active_only=False)
    return render_template('channels/index.html', channels=channels)

@channels_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Добавление нового канала"""
    if request.method == 'POST':
        channel_username = request.form.get('channel_username')
        
        if not channel_username:
            flash('Введите имя пользователя канала.')
            return redirect(url_for('channels.add'))
        
        # Проверяем, начинается ли имя пользователя с @
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
        
        # Проверяем, существует ли уже такой канал
        database = current_app.config['DATABASE']
        existing_channel = database.get_channel_by_username(channel_username)
        
        if existing_channel:
            flash(f'Канал {channel_username} уже добавлен.')
            return redirect(url_for('channels.index'))
        
        # Получаем экземпляр бота
        bot = current_app.config.get('BOT')
        
        if not bot or not bot.running:
            flash('Бот не запущен. Невозможно добавить канал.')
            return redirect(url_for('channels.index'))
        
        # Добавляем канал
        success = asyncio.run(bot.join_channel(channel_username))
        
        if success:
            flash(f'Канал {channel_username} успешно добавлен.')
        else:
            flash(f'Ошибка при добавлении канала {channel_username}.')
        
        return redirect(url_for('channels.index'))
    
    return render_template('channels/add.html')

@channels_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Удаление канала"""
    database = current_app.config['DATABASE']
    channel = database.get_channel_by_id(id)
    
    if not channel:
        flash('Канал не найден.')
        return redirect(url_for('channels.index'))
    
    # Получаем экземпляр бота
    bot = current_app.config.get('BOT')
    
    if not bot or not bot.running:
        flash('Бот не запущен. Невозможно удалить канал.')
        return redirect(url_for('channels.index'))
    
    # Удаляем канал
    success = asyncio.run(bot.leave_channel(channel.id))
    
    if success:
        flash(f'Канал {channel.channel_name} успешно удален.')
    else:
        # Если не удалось отписаться от канала, просто деактивируем его
        database.update_channel(channel.id, is_active=False)
        flash(f'Канал {channel.channel_name} деактивирован.')
    
    return redirect(url_for('channels.index'))

@channels_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    """Включение/выключение мониторинга канала"""
    database = current_app.config['DATABASE']
    channel = database.get_channel_by_id(id)
    
    if not channel:
        flash('Канал не найден.')
        return redirect(url_for('channels.index'))
    
    # Инвертируем статус активности
    new_status = not channel.is_active
    database.update_channel(channel.id, is_active=new_status)
    
    status_text = 'активирован' if new_status else 'деактивирован'
    flash(f'Канал {channel.channel_name} {status_text}.')
    
    return redirect(url_for('channels.index'))

@channels_bp.route('/<int:id>/posts')
@login_required
def posts(id):
    """Просмотр постов канала"""
    database = current_app.config['DATABASE']
    channel = database.get_channel_by_id(id)
    
    if not channel:
        flash('Канал не найден.')
        return redirect(url_for('channels.index'))
    
    posts = database.get_posts(channel_id=channel.id)
    
    return render_template('channels/posts.html', channel=channel, posts=posts)
