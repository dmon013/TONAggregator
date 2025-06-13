# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Загружает переменные из файла.env в каталоге backend или корне проекта

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    
    # Путь к вашему JSON-файлу ключа сервисного аккаунта Firebase
    # Для безопасности этот путь также может быть переменной окружения
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH') or "serviceAccountKey.json"
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN_BACKEND') # Для валидации initData

    # Добавьте другие конфигурации по мере необходимости
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Создайте файл.env в каталоге backend/ или корне проекта:
# FLASK_SECRET_KEY=ваш_секретный_ключ_flask
# FIREBASE_SERVICE_ACCOUNT_KEY_PATH=путь/к/вашему/serviceAccountKey.json (может быть относительным к каталогу backend)
# TELEGRAM_BOT_TOKEN_BACKEND=ваш_токен_telegram_бота (тот же, что и для bot.js)
# FLASK_DEBUG=True (для разработки)