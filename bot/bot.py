from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

from bot.config import API_ID, API_HASH, SESSION_NAME, CHECK_INTERVAL

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Основной класс Telegram бота для мониторинга каналов и добавления комментариев"""
    
    def __init__(self, database, session_name=SESSION_NAME):
        """Инициализация бота"""
        self.database = database
        self.client = None
        self.session_name = session_name
        self.running = False
        self.check_interval = CHECK_INTERVAL
        self.monitor_task = None
    
    async def start(self):
        """Запуск бота"""
        if self.running:
            logger.warning("Бот уже запущен")
            return
        
        # Создаем клиент Telegram
        self.client = TelegramClient(self.session_name, API_ID, API_HASH)
        
        # Запускаем клиент
        await self.client.start()
        
        # Проверяем авторизацию
        if not await self.client.is_user_authorized():
            logger.error("Пользователь не авторизован. Необходимо выполнить вход.")
            return False
        
        logger.info("Бот успешно запущен")
        self.running = True
        
        # Запускаем задачу мониторинга каналов
        self.monitor_task = asyncio.create_task(self.monitor_channels())
        
        return True
    
    async def stop(self):
        """Остановка бота"""
        if not self.running:
            logger.warning("Бот не запущен")
            return
        
        # Отменяем задачу мониторинга
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        # Отключаемся от Telegram
        await self.client.disconnect()
        
        logger.info("Бот остановлен")
        self.running = False
    
    async def join_channel(self, channel_username):
        """Подписка на канал"""
        if not self.running:
            logger.error("Бот не запущен")
            return False
        
        try:
            # Получаем информацию о канале
            channel_entity = await self.client.get_entity(channel_username)
            
            # Подписываемся на канал
            await self.client(JoinChannelRequest(channel_entity))
            
            # Добавляем канал в базу данных
            self.database.add_channel(
                channel_id=str(channel_entity.id),
                channel_name=channel_entity.title,
                channel_username=channel_username
            )
            
            logger.info(f"Успешно подписались на канал {channel_username}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при подписке на канал {channel_username}: {e}")
            return False
    
    async def leave_channel(self, channel_id):
        """Отписка от канала"""
        if not self.running:
            logger.error("Бот не запущен")
            return False
        
        try:
            # Получаем канал из базы данных
            channel = self.database.get_channel_by_id(channel_id)
            if not channel:
                logger.error(f"Канал с ID {channel_id} не найден")
                return False
            
            # Получаем сущность канала
            channel_entity = await self.client.get_entity(int(channel.channel_id))
            
            # Отписываемся от канала
            await self.client.delete_dialog(channel_entity)
            
            # Обновляем статус канала в базе данных
            self.database.update_channel(channel.id, is_active=False)
            
            logger.info(f"Успешно отписались от канала {channel.channel_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отписке от канала {channel_id}: {e}")
            return False
    
    async def get_channel_posts(self, channel_id, limit=10):
        """Получение последних постов из канала"""
        if not self.running:
            logger.error("Бот не запущен")
            return []
        
        try:
            # Получаем канал из базы данных
            channel = self.database.get_channel_by_id(channel_id)
            if not channel:
                logger.error(f"Канал с ID {channel_id} не найден")
                return []
            
            # Получаем сущность канала
            channel_entity = await self.client.get_entity(int(channel.channel_id))
            
            # Получаем историю сообщений
            posts = await self.client(GetHistoryRequest(
                peer=channel_entity,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            
            return posts.messages
        except Exception as e:
            logger.error(f"Ошибка при получении постов из канала {channel_id}: {e}")
            return []
    
    async def add_comment(self, post_id, comment_text):
        """Добавление комментария к посту"""
        if not self.running:
            logger.error("Бот не запущен")
            return False
        
        try:
            # Получаем пост из базы данных
            post = self.database.get_post_by_id(post_id)
            if not post:
                logger.error(f"Пост с ID {post_id} не найден")
                return False
            
            # Получаем канал
            channel = self.database.get_channel_by_id(post.channel_id)
            if not channel:
                logger.error(f"Канал для поста {post_id} не найден")
                return False
            
            # Получаем сущность канала
            channel_entity = await self.client.get_entity(int(channel.channel_id))
            
            # Отправляем комментарий
            comment = await self.client.send_message(
                entity=channel_entity,
                message=comment_text,
                comment_to=post.message_id
            )
            
            # Создаем запись о комментарии в базе данных
            comment_obj = self.database.add_comment(comment_text)
            post_comment = self.database.add_post_comment(
                post_id=post.id,
                comment_id=comment_obj.id,
                status='sent'
            )
            
            # Обновляем ID сообщения комментария
            self.database.update_post_comment(
                post_comment.id,
                comment_message_id=comment.id
            )
            
            logger.info(f"Успешно добавлен комментарий к посту {post_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария к посту {post_id}: {e}")
            return False
    
    async def monitor_channels(self):
        """Мониторинг каналов на наличие новых постов"""
        logger.info("Запущен мониторинг каналов")
        
        while self.running:
            try:
                # Получаем список активных каналов
                channels = self.database.get_channels(active_only=True)
                
                for channel in channels:
                    # Получаем последние посты из канала
                    posts = await self.get_channel_posts(channel.id, limit=10)
                    
                    for post in posts:
                        # Проверяем, есть ли пост в базе данных
                        existing_post = self.database.get_post_by_id(post.id)
                        if not existing_post:
                            # Добавляем новый пост в базу данных
                            self.database.add_post(
                                channel_id=channel.id,
                                message_id=post.id,
                                content=post.message,
                                posted_at=post.date
                            )
                            
                            logger.info(f"Обнаружен новый пост в канале {channel.channel_name}")
                
                # Ждем указанный интервал перед следующей проверкой
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                # Задача отменена
                break
            except Exception as e:
                logger.error(f"Ошибка при мониторинге каналов: {e}")
                # Ждем перед повторной попыткой
                await asyncio.sleep(10)
        
        logger.info("Мониторинг каналов остановлен")
