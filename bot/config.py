# Конфигурация Telegram бота
# Здесь хранятся настройки для подключения к Telegram API

# Данные для авторизации в Telegram API
# Получите их на https://my.telegram.org/apps
API_ID = "YOUR_API_ID"  # Заменить на реальный API ID
API_HASH = "YOUR_API_HASH"  # Заменить на реальный API Hash

# Настройки сессии
SESSION_NAME = "telegram_bot_session"

# Настройки базы данных
DATABASE_PATH = "data/telegram_bot.db"

# Настройки мониторинга
CHECK_INTERVAL = 60  # Интервал проверки новых постов в секундах

# Настройки очистки данных
CLEANUP_DAYS = 3  # Количество дней хранения данных

# Настройки админ-панели
ADMIN_PASSWORD = "123456"  # Начальный пароль для входа в админ-панель
ADMIN_PORT = 5000  # Порт для запуска админ-панели
