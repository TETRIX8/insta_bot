from bot.channel_monitor import ChannelMonitor
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

class ChannelMonitor:
    """Класс для мониторинга каналов и обнаружения новых постов"""
    
    def __init__(self, client, database):
        """Инициализация монитора каналов"""
        self.client = client
        self.database = database
    
    async def get_channel_posts(self, channel_id, limit=10):
        """Получение последних постов из канала"""
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
    
    async def check_new_posts(self):
        """Проверка новых постов во всех активных каналах"""
        try:
            # Получаем список активных каналов
            channels = self.database.get_channels(active_only=True)
            
            new_posts_count = 0
            
            for channel in channels:
                # Получаем последние посты из канала
                posts = await self.get_channel_posts(channel.id, limit=10)
                
                for post in posts:
                    # Проверяем, есть ли пост в базе данных
                    existing_post = self.database.get_post_by_message_id(channel.id, post.id)
                    if not existing_post:
                        # Добавляем новый пост в базу данных
                        content = post.message if hasattr(post, 'message') else ""
                        self.database.add_post(
                            channel_id=channel.id,
                            message_id=post.id,
                            content=content,
                            posted_at=post.date
                        )
                        
                        new_posts_count += 1
                        logger.info(f"Обнаружен новый пост в канале {channel.channel_name}")
            
            return new_posts_count
        except Exception as e:
            logger.error(f"Ошибка при проверке новых постов: {e}")
            return 0
