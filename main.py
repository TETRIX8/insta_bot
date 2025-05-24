import os
import sys
import asyncio
from threading import Thread
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# Добавляем корневую директорию проекта в путь импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data.database import Database
from bot.bot import TelegramBot
from bot.channel_monitor import ChannelMonitor
from bot.comment_manager import CommentManager
from admin_panel.app import create_app
from bot.config import DATABASE_PATH, ADMIN_PORT, CHECK_INTERVAL, CLEANUP_DAYS

def run_async_loop(loop):
    """Запуск асинхронного цикла событий в отдельном потоке"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    """Основная функция для запуска приложения"""
    # Инициализируем базу данных
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_PATH)
    database = Database(db_path)
    
    # Инициализируем бота
    bot = TelegramBot(database)
    
    # Инициализируем компоненты бота
    bot.channel_monitor = ChannelMonitor(bot.client, database)
    bot.comment_manager = CommentManager(bot.client, database)
    
    # Создаем асинхронный цикл событий
    loop = asyncio.new_event_loop()
    
    # Запускаем асинхронный цикл в отдельном потоке
    thread = Thread(target=run_async_loop, args=(loop,), daemon=True)
    thread.start()
    
    # Создаем Flask приложение
    app = create_app(database)
    
    # Добавляем бота в конфигурацию приложения
    app.config['BOT'] = bot
    
    # Инициализируем планировщик задач
    scheduler = BackgroundScheduler()
    
    # Добавляем задачу для очистки старых данных
    cleanup_days = int(database.get_setting('cleanup_days', default=CLEANUP_DAYS))
    scheduler.add_job(database.cleanup_old_data, 'interval', days=1, args=[cleanup_days])
    
    # Запускаем планировщик
    scheduler.start()
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=ADMIN_PORT, debug=False)

if __name__ == '__main__':
    main()
