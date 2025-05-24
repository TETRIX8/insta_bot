from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Channel(Base):
    """Модель для хранения информации о каналах для мониторинга"""
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(255), nullable=False, unique=True)  # ID канала в Telegram
    channel_name = Column(String(255), nullable=False)  # Название канала
    channel_username = Column(String(255))  # Username канала (если есть)
    is_active = Column(Boolean, default=True)  # Активен ли мониторинг
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    posts = relationship("Post", back_populates="channel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.channel_name})>"


class Post(Base):
    """Модель для хранения информации о постах из каналов"""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    message_id = Column(Integer, nullable=False)  # ID сообщения в Telegram
    content = Column(Text)  # Содержание поста
    posted_at = Column(DateTime)  # Время публикации поста
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    channel = relationship("Channel", back_populates="posts")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post(id={self.id}, message_id={self.message_id})>"


class Comment(Base):
    """Модель для хранения шаблонов комментариев"""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)  # Текст комментария
    description = Column(String(255))  # Описание комментария
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    post_comments = relationship("PostComment", back_populates="comment")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, description={self.description})>"


class PostComment(Base):
    """Модель для связи между постами и добавленными комментариями"""
    __tablename__ = 'post_comments'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=False)
    comment_message_id = Column(Integer)  # ID комментария в Telegram
    status = Column(String(50), default='pending')  # Статус комментария (pending, sent, failed)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    post = relationship("Post", back_populates="comments")
    comment = relationship("Comment", back_populates="post_comments")
    
    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id}, comment_id={self.comment_id})>"


class Setting(Base):
    """Модель для хранения настроек бота и админ-панели"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True)  # Ключ настройки
    value = Column(Text)  # Значение настройки
    description = Column(String(255))  # Описание настройки
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Setting(key={self.key}, value={self.value})>"


# Функция для инициализации базы данных
def init_db(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine
