from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
import asyncio

# Создаем Blueprint для настроек
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def index():
    """Страница настроек"""
    database = current_app.config['DATABASE']
    
    # Получаем текущие настройки
    check_interval = database.get_setting('check_interval', default='60')
    cleanup_days = database.get_setting('cleanup_days', default='3')
    
    return render_template('settings/index.html', 
                          check_interval=check_interval,
                          cleanup_days=cleanup_days)

@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    """Обновление настроек"""
    check_interval = request.form.get('check_interval', '60')
    cleanup_days = request.form.get('cleanup_days', '3')
    
    # Проверяем корректность значений
    try:
        check_interval_int = int(check_interval)
        if check_interval_int < 10:
            flash('Интервал проверки должен быть не менее 10 секунд.')
            return redirect(url_for('settings.index'))
    except ValueError:
        flash('Интервал проверки должен быть числом.')
        return redirect(url_for('settings.index'))
    
    try:
        cleanup_days_int = int(cleanup_days)
        if cleanup_days_int < 1:
            flash('Период хранения данных должен быть не менее 1 дня.')
            return redirect(url_for('settings.index'))
    except ValueError:
        flash('Период хранения данных должен быть числом.')
        return redirect(url_for('settings.index'))
    
    # Сохраняем настройки
    database = current_app.config['DATABASE']
    database.set_setting('check_interval', check_interval, 'Интервал проверки новых постов (в секундах)')
    database.set_setting('cleanup_days', cleanup_days, 'Период хранения данных (в днях)')
    
    # Обновляем настройки бота, если он запущен
    bot = current_app.config.get('BOT')
    if bot and bot.running:
        bot.check_interval = check_interval_int
    
    flash('Настройки успешно обновлены.')
    return redirect(url_for('settings.index'))

@settings_bp.route('/bot/start', methods=['POST'])
@login_required
def start_bot():
    """Запуск бота"""
    bot = current_app.config.get('BOT')
    
    if not bot:
        flash('Бот не инициализирован.')
        return redirect(url_for('settings.index'))
    
    if bot.running:
        flash('Бот уже запущен.')
        return redirect(url_for('settings.index'))
    
    # Запускаем бота
    success = asyncio.run(bot.start())
    
    if success:
        flash('Бот успешно запущен.')
    else:
        flash('Ошибка при запуске бота.')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/bot/stop', methods=['POST'])
@login_required
def stop_bot():
    """Остановка бота"""
    bot = current_app.config.get('BOT')
    
    if not bot:
        flash('Бот не инициализирован.')
        return redirect(url_for('settings.index'))
    
    if not bot.running:
        flash('Бот не запущен.')
        return redirect(url_for('settings.index'))
    
    # Останавливаем бота
    asyncio.run(bot.stop())
    
    flash('Бот остановлен.')
    return redirect(url_for('settings.index'))

@settings_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup():
    """Ручная очистка старых данных"""
    database = current_app.config['DATABASE']
    cleanup_days = int(database.get_setting('cleanup_days', default='3'))
    
    # Выполняем очистку
    database.cleanup_old_data(days=cleanup_days)
    
    flash(f'Данные старше {cleanup_days} дней успешно удалены.')
    return redirect(url_for('settings.index'))
