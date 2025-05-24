from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
import asyncio

# Создаем Blueprint для управления комментариями
comments_bp = Blueprint('comments', __name__, url_prefix='/comments')

@comments_bp.route('/')
@login_required
def index():
    """Страница со списком шаблонов комментариев"""
    database = current_app.config['DATABASE']
    comments = database.get_comments()
    return render_template('comments/index.html', comments=comments)

@comments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Добавление нового шаблона комментария"""
    if request.method == 'POST':
        text = request.form.get('text')
        description = request.form.get('description')
        
        if not text:
            flash('Введите текст комментария.')
            return redirect(url_for('comments.add'))
        
        # Добавляем комментарий в базу данных
        database = current_app.config['DATABASE']
        database.add_comment(text, description)
        
        flash('Шаблон комментария успешно добавлен.')
        return redirect(url_for('comments.index'))
    
    return render_template('comments/add.html')

@comments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Редактирование шаблона комментария"""
    database = current_app.config['DATABASE']
    comment = database.get_comment_by_id(id)
    
    if not comment:
        flash('Шаблон комментария не найден.')
        return redirect(url_for('comments.index'))
    
    if request.method == 'POST':
        text = request.form.get('text')
        description = request.form.get('description')
        
        if not text:
            flash('Введите текст комментария.')
            return redirect(url_for('comments.edit', id=id))
        
        # Обновляем комментарий
        database.update_comment(id, text=text, description=description)
        
        flash('Шаблон комментария успешно обновлен.')
        return redirect(url_for('comments.index'))
    
    return render_template('comments/edit.html', comment=comment)

@comments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Удаление шаблона комментария"""
    database = current_app.config['DATABASE']
    comment = database.get_comment_by_id(id)
    
    if not comment:
        flash('Шаблон комментария не найден.')
        return redirect(url_for('comments.index'))
    
    # Удаляем комментарий
    database.delete_comment(id)
    
    flash('Шаблон комментария успешно удален.')
    return redirect(url_for('comments.index'))

@comments_bp.route('/post/<int:post_id>')
@login_required
def post_comments(post_id):
    """Просмотр комментариев к посту"""
    database = current_app.config['DATABASE']
    post = database.get_post_by_id(post_id)
    
    if not post:
        flash('Пост не найден.')
        return redirect(url_for('channels.index'))
    
    # Получаем канал
    channel = database.get_channel_by_id(post.channel_id)
    
    # Получаем комментарии к посту
    post_comments = database.get_post_comments(post_id=post_id)
    
    # Получаем шаблоны комментариев
    comments = database.get_comments()
    
    return render_template('comments/post_comments.html', 
                          post=post, 
                          channel=channel, 
                          post_comments=post_comments, 
                          comments=comments)

@comments_bp.route('/post/<int:post_id>/add', methods=['POST'])
@login_required
def add_to_post(post_id):
    """Добавление комментария к посту"""
    comment_id = request.form.get('comment_id')
    custom_text = request.form.get('custom_text')
    
    database = current_app.config['DATABASE']
    post = database.get_post_by_id(post_id)
    
    if not post:
        flash('Пост не найден.')
        return redirect(url_for('channels.index'))
    
    # Получаем экземпляр бота
    bot = current_app.config.get('BOT')
    
    if not bot or not bot.running:
        flash('Бот не запущен. Невозможно добавить комментарий.')
        return redirect(url_for('comments.post_comments', post_id=post_id))
    
    # Определяем текст комментария
    comment_text = custom_text
    if comment_id and not custom_text:
        comment = database.get_comment_by_id(comment_id)
        if comment:
            comment_text = comment.text
    
    if not comment_text:
        flash('Введите текст комментария.')
        return redirect(url_for('comments.post_comments', post_id=post_id))
    
    # Добавляем комментарий
    comment_manager = bot.comment_manager
    success, message = asyncio.run(comment_manager.add_comment_to_post(post_id, comment_text))
    
    if success:
        flash('Комментарий успешно добавлен к посту.')
    else:
        flash(f'Ошибка при добавлении комментария: {message}')
    
    return redirect(url_for('comments.post_comments', post_id=post_id))

@comments_bp.route('/post_comment/<int:post_comment_id>/delete', methods=['POST'])
@login_required
def delete_from_post(post_comment_id):
    """Удаление комментария из поста"""
    database = current_app.config['DATABASE']
    post_comment = database.get_post_comment_by_id(post_comment_id)
    
    if not post_comment:
        flash('Комментарий не найден.')
        return redirect(url_for('channels.index'))
    
    post_id = post_comment.post_id
    
    # Получаем экземпляр бота
    bot = current_app.config.get('BOT')
    
    if not bot or not bot.running:
        flash('Бот не запущен. Невозможно удалить комментарий.')
        return redirect(url_for('comments.post_comments', post_id=post_id))
    
    # Удаляем комментарий
    comment_manager = bot.comment_manager
    success, message = asyncio.run(comment_manager.delete_comment(post_comment_id))
    
    if success:
        flash('Комментарий успешно удален из поста.')
    else:
        flash(f'Ошибка при удалении комментария: {message}')
    
    return redirect(url_for('comments.post_comments', post_id=post_id))
