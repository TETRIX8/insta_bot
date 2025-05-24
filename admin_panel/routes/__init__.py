from flask import Blueprint

# Создаем Blueprint для маршрутов
channels_bp = Blueprint('channels', __name__, url_prefix='/channels')
comments_bp = Blueprint('comments', __name__, url_prefix='/comments')
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')
