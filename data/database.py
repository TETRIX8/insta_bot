import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta

from data.models import Base, Channel, Post, Comment, PostComment, Setting

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path):
        """Инициализация подключения к базе данных"""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def get_session(self):
        """Получение сессии для работы с базой данных"""
        return self.Session()
    
    def close_session(self):
        """Закрытие сессии"""
        self.Session.remove()
    
    # Методы для работы с каналами
    def add_channel(self, channel_id, channel_name, channel_username=None):
        """Добавление нового канала для мониторинга"""
        session = self.get_session()
        try:
            channel = Channel(
                channel_id=channel_id,
                channel_name=channel_name,
                channel_username=channel_username,
                is_active=True
            )
            session.add(channel)
            session.commit()
            return channel
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def get_channels(self, active_only=True):
        """Получение списка каналов для мониторинга"""
        session = self.get_session()
        try:
            if active_only:
                return session.query(Channel).filter(Channel.is_active == True).all()
            return session.query(Channel).all()
        finally:
            self.close_session()
    
    def get_channel_by_id(self, channel_id):
        """Получение канала по ID"""
        session = self.get_session()
        try:
            return session.query(Channel).filter(Channel.channel_id == channel_id).first()
        finally:
            self.close_session()
    
    def update_channel(self, id, **kwargs):
        """Обновление информации о канале"""
        session = self.get_session()
        try:
            channel = session.query(Channel).filter(Channel.id == id).first()
            if channel:
                for key, value in kwargs.items():
                    if hasattr(channel, key):
                        setattr(channel, key, value)
                session.commit()
                return channel
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def delete_channel(self, id):
        """Удаление канала"""
        session = self.get_session()
        try:
            channel = session.query(Channel).filter(Channel.id == id).first()
            if channel:
                session.delete(channel)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    # Методы для работы с постами
    def add_post(self, channel_id, message_id, content, posted_at):
        """Добавление нового поста"""
        session = self.get_session()
        try:
            post = Post(
                channel_id=channel_id,
                message_id=message_id,
                content=content,
                posted_at=posted_at
            )
            session.add(post)
            session.commit()
            return post
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def get_posts(self, channel_id=None, limit=100):
        """Получение списка постов"""
        session = self.get_session()
        try:
            query = session.query(Post)
            if channel_id:
                query = query.filter(Post.channel_id == channel_id)
            return query.order_by(Post.posted_at.desc()).limit(limit).all()
        finally:
            self.close_session()
    
    def get_post_by_id(self, post_id):
        """Получение поста по ID"""
        session = self.get_session()
        try:
            return session.query(Post).filter(Post.id == post_id).first()
        finally:
            self.close_session()
    
    # Методы для работы с комментариями
    def add_comment(self, text, description=None):
        """Добавление нового шаблона комментария"""
        session = self.get_session()
        try:
            comment = Comment(
                text=text,
                description=description
            )
            session.add(comment)
            session.commit()
            return comment
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def get_comments(self):
        """Получение списка шаблонов комментариев"""
        session = self.get_session()
        try:
            return session.query(Comment).all()
        finally:
            self.close_session()
    
    def get_comment_by_id(self, comment_id):
        """Получение шаблона комментария по ID"""
        session = self.get_session()
        try:
            return session.query(Comment).filter(Comment.id == comment_id).first()
        finally:
            self.close_session()
    
    def update_comment(self, id, **kwargs):
        """Обновление шаблона комментария"""
        session = self.get_session()
        try:
            comment = session.query(Comment).filter(Comment.id == id).first()
            if comment:
                for key, value in kwargs.items():
                    if hasattr(comment, key):
                        setattr(comment, key, value)
                session.commit()
                return comment
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def delete_comment(self, id):
        """Удаление шаблона комментария"""
        session = self.get_session()
        try:
            comment = session.query(Comment).filter(Comment.id == id).first()
            if comment:
                session.delete(comment)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    # Методы для работы с комментариями к постам
    def add_post_comment(self, post_id, comment_id, status='pending'):
        """Добавление комментария к посту"""
        session = self.get_session()
        try:
            post_comment = PostComment(
                post_id=post_id,
                comment_id=comment_id,
                status=status
            )
            session.add(post_comment)
            session.commit()
            return post_comment
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def update_post_comment(self, id, **kwargs):
        """Обновление информации о комментарии к посту"""
        session = self.get_session()
        try:
            post_comment = session.query(PostComment).filter(PostComment.id == id).first()
            if post_comment:
                for key, value in kwargs.items():
                    if hasattr(post_comment, key):
                        setattr(post_comment, key, value)
                session.commit()
                return post_comment
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    def get_post_comments(self, post_id=None, status=None):
        """Получение комментариев к постам"""
        session = self.get_session()
        try:
            query = session.query(PostComment)
            if post_id:
                query = query.filter(PostComment.post_id == post_id)
            if status:
                query = query.filter(PostComment.status == status)
            return query.all()
        finally:
            self.close_session()
    
    # Методы для работы с настройками
    def get_setting(self, key, default=None):
        """Получение значения настройки по ключу"""
        session = self.get_session()
        try:
            setting = session.query(Setting).filter(Setting.key == key).first()
            return setting.value if setting else default
        finally:
            self.close_session()
    
    def set_setting(self, key, value, description=None):
        """Установка значения настройки"""
        session = self.get_session()
        try:
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
                if description:
                    setting.description = description
            else:
                setting = Setting(
                    key=key,
                    value=value,
                    description=description
                )
                session.add(setting)
            session.commit()
            return setting
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
    
    # Метод для очистки старых данных
    def cleanup_old_data(self, days=3):
        """Удаление данных старше указанного количества дней"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Получаем старые посты
            old_posts = session.query(Post).filter(Post.created_at < cutoff_date).all()
            
            # Удаляем связанные комментарии и сами посты
            for post in old_posts:
                session.query(PostComment).filter(PostComment.post_id == post.id).delete()
            
            # Удаляем старые посты
            session.query(Post).filter(Post.created_at < cutoff_date).delete()
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session()
