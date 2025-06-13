# backend/routes/users.py
from flask import Blueprint, jsonify
from backend.extensions import firebase_db
from backend.utils.auth import validate_telegram_data
import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@validate_telegram_data
def get_me(telegram_user):
    user_id = str(telegram_user.get('id'))
    user_ref = firebase_db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        return jsonify(user_doc.to_dict()), 200
    else:
        # Создаем профиль пользователя при первом доступе
        user_data = {
            "telegram_id": telegram_user.get('id'),
            "username": telegram_user.get('username'),
            "first_name": telegram_user.get('first_name'),
            "favorites": [],
            "recentlyOpened": [], # ИЗМЕНЕНИЕ: новое поле
            "votedApps": [],      # ИЗМЕНЕНИЕ: новое поле
            "role": "user",    # ИЗМЕНЕНИЕ: роль по умолчанию
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z"
        }
        user_ref.set(user_data)
        return jsonify(user_data), 201

# ИЗМЕНЕНИЕ: Новый эндпоинт для получения недавно открытых приложений
@users_bp.route('/me/recent', methods=['GET'])
@validate_telegram_data
def get_my_recent_apps(telegram_user):
    user_id = str(telegram_user.get('id'))
    user_doc = firebase_db.collection('users').document(user_id).get()
    if user_doc.exists:
        # Получаем ID в порядке от нового к старому, берем первые 10
        recent_ids = user_doc.to_dict().get('recentlyOpened', [])[::-1][:10]
        recent_apps = []
        if recent_ids:
            app_refs = [firebase_db.collection('apps').document(app_id) for app_id in recent_ids]
            app_docs = firebase_db.get_all(app_refs)
            for doc in app_docs:
                if doc.exists:
                    app_data = doc.to_dict()
                    app_data['id'] = doc.id
                    recent_apps.append(app_data)
        return jsonify(recent_apps), 200
    return jsonify(), 200

# (Эндпоинты для избранного остаются без изменений)