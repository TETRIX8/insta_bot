from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio
import logging
from datetime import datetime

from bot.config import API_ID, API_HASH, SESSION_NAME

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CommentManager:
    """Класс для управления комментариями к постам"""
    
    def __init__(self, client, database):
        """Инициализация менеджера комментариев"""
        self.client = client
        self.database = database
    
    async def add_comment_to_post(self, post_id, comment_text):
        """Добавление комментария к посту"""
        try:
            # Получаем пост из базы данных
            post = self.database.get_post_by_id(post_id)
            if not post:
                logger.error(f"Пост с ID {post_id} не найден")
                return False, "Пост не найден"
            
            # Получаем канал
            channel = self.database.get_channel_by_id(post.channel_id)
            if not channel:
                logger.error(f"Канал для поста {post_id} не найден")
                return False, "Канал не найден"
            
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
            return True, "Комментарий успешно добавлен"
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария к посту {post_id}: {e}")
            return False, f"Ошибка: {str(e)}"
    
    async def delete_comment(self, post_comment_id):
        """Удаление комментария"""
        try:
            # Получаем комментарий из базы данных
            post_comment = self.database.get_post_comment_by_id(post_comment_id)
            if not post_comment:
                logger.error(f"Комментарий с ID {post_comment_id} не найден")
                return False, "Комментарий не найден"
            
            # Получаем пост
            post = self.database.get_post_by_id(post_comment.post_id)
            if not post:
                logger.error(f"Пост для комментария {post_comment_id} не найден")
                return False, "Пост не найден"
            
            # Получаем канал
            channel = self.database.get_channel_by_id(post.channel_id)
            if not channel:
                logger.error(f"Канал для поста {post.id} не найден")
                return False, "Канал не найден"
            
            # Получаем сущность канала
            channel_entity = await self.client.get_entity(int(channel.channel_id))
            
            # Удаляем комментарий в Telegram
            if post_comment.comment_message_id:
                await self.client.delete_messages(
                    entity=channel_entity,
                    message_ids=[post_comment.comment_message_id]
                )
            
            # Обновляем статус комментария в базе данных
            self.database.update_post_comment(
                post_comment.id,
                status='deleted'
            )
            
            logger.info(f"Успешно удален комментарий {post_comment_id}")
            return True, "Комментарий успешно удален"
        except Exception as e:
            logger.error(f"Ошибка при удалении комментария {post_comment_id}: {e}")
            return False, f"Ошибка: {str(e)}"
    
    async def get_comments_for_post(self, post_id):
        """Получение комментариев к посту"""
        try:
            # Получаем пост из базы данных
            post = self.database.get_post_by_id(post_id)
            if not post:
                logger.error(f"Пост с ID {post_id} не найден")
                return []
            
            # Получаем канал
            channel = self.database.get_channel_by_id(post.channel_id)
            if not channel:
                logger.error(f"Канал для поста {post_id} не найден")
                return []
            
            # Получаем сущность канала
            channel_entity = await self.client.get_entity(int(channel.channel_id))
            
            # Получаем комментарии к посту
            comments = await self.client.get_messages(
                entity=channel_entity,
                reply_to=post.message_id
            )
            
            return comments
        except Exception as e:
            logger.error(f"Ошибка при получении комментариев к посту {post_id}: {e}")
            return []
