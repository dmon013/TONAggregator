# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS

from.config import Config
from.extensions import firebase_db, initialize_firebase # firebase_db импортируется, но используется после инициализации
from.utils.auth import validate_telegram_data # Предполагается, что вы создадите это

# Импорт Blueprints
from.routes.apps import apps_bp
from.routes.categories import categories_bp
from.routes.reviews import reviews_bp
from.routes.users import users_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация Firebase Admin SDK
    initialize_firebase(app.config.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"))

    # Включение CORS для локальной разработки (ограничить в продакшене)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Будьте более конкретны в продакшене

    # Регистрация Blueprints
    app.register_blueprint(apps_bp, url_prefix='/api/apps')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Backend работает!"}), 200

    return app