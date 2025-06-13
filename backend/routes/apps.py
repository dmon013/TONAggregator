# backend/routes/apps.py
from flask import Blueprint, jsonify, request
from backend.extensions import firebase_db
from backend.utils.auth import validate_telegram_data, admin_required # ИЗМЕНЕНИЕ: импортируем новый декоратор
from firebase_admin import firestore
import datetime

apps_bp = Blueprint('apps', __name__)

# --- Публичные эндпоинты ---

@apps_bp.route('/', methods=['GET'])
@validate_telegram_data
def get_apps_list(telegram_user):
    """
    Основной эндпоинт для получения списка приложений.
    Поддерживает поиск по названию и фильтрацию по категории.
    """
    try:
        query = firebase_db.collection('apps')
        
        category_id = request.args.get('category_id')
        search_query = request.args.get('q')

        if category_id:
            query = query.where('categories', 'array_contains', category_id)
        
        # ИЗМЕНЕНИЕ: Для поиска используется префиксный поиск.
        # Firestore не поддерживает полнотекстовый поиск "из коробки".
        # Этот метод ищет документы, где поле 'name' начинается с поискового запроса.
        if search_query:
            query = query.order_by('name').start_at(search_query).end_at(search_query + '\uf8ff')
        else:
            # Если нет поиска, сортируем по имени по умолчанию
            query = query.order_by('name')

        apps_list = []
        for doc in query.stream():
            app_data = doc.to_dict()
            app_data['id'] = doc.id
            apps_list.append(app_data)
            
        return jsonify(apps_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@apps_bp.route('/<app_id>', methods=['GET'])
@validate_telegram_data
def get_app_by_id(telegram_user, app_id):
    try:
        app_doc = firebase_db.collection('apps').document(app_id).get()
        if app_doc.exists:
            app_data = app_doc.to_dict()
            app_data['id'] = app_doc.id
            return jsonify(app_data), 200
        else:
            return jsonify({"error": "Приложение не найдено"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ИЗМЕНЕНИЕ: Эндпоинт для логирования открытия приложения
@apps_bp.route('/<app_id>/open', methods=['POST'])
@validate_telegram_data
def open_app(telegram_user, app_id):
    user_id = str(telegram_user.get('id'))
    try:
        # 1. Увеличиваем счетчик запусков приложения
        app_ref = firebase_db.collection('apps').document(app_id)
        app_ref.update({'usageCount': firestore.Increment(1)})

        # 2. Обновляем список недавно открытых у пользователя
        user_ref = firebase_db.collection('users').document(user_id)
        # Атомарно добавляем ID в начало массива и удаляем старые
        user_ref.update({
            'recentlyOpened': firestore.ArrayUnion([app_id])
        })
        # Чтобы список не рос бесконечно, можно периодически обрезать его
        # (например, в Cloud Function или при чтении), здесь для простоты опускаем.

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ИЗМЕНЕНИЕ: Эндпоинт для голосования
@apps_bp.route('/<app_id>/vote', methods=['POST'])
@validate_telegram_data
def vote_for_app(telegram_user, app_id):
    user_id = str(telegram_user.get('id'))
    user_ref = firebase_db.collection('users').document(user_id)
    
    # Проверяем, голосовал ли пользователь уже
    user_doc = user_ref.get()
    if user_doc.exists and app_id in user_doc.to_dict().get('votedApps', ):
        return jsonify({"error": "Вы уже голосовали за это приложение"}), 409 # 409 Conflict

    try:
        # Используем транзакцию для атомарного обновления
        @firestore.transactional
        def update_in_transaction(transaction, app_ref_param, user_ref_param):
            # Увеличиваем счетчик голосов у приложения
            transaction.update(app_ref_param, {'votesCount': firestore.Increment(1)})
            # Добавляем ID приложения в список проголосовавших у пользователя
            transaction.update(user_ref_param, {'votedApps': firestore.ArrayUnion([app_id])})

        app_ref = firebase_db.collection('apps').document(app_id)
        transaction = firebase_db.transaction()
        update_in_transaction(transaction, app_ref, user_ref)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Админ-эндпоинты ---

@apps_bp.route('/', methods=['POST'])
@admin_required
def add_app(telegram_user):
    try:
        app_data = request.get_json()
        # Добавляем системные поля
        app_data['createdAt'] = firestore.SERVER_TIMESTAMP
        app_data['usageCount'] = 0
        app_data['votesCount'] = 0
        # Валидация данных (в реальном приложении)
        #...
        _, new_app_ref = firebase_db.collection('apps').add(app_data)
        return jsonify({"id": new_app_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@apps_bp.route('/<app_id>', methods=['PUT'])
@admin_required
def update_app(telegram_user, app_id):
    try:
        app_data = request.get_json()
        firebase_db.collection('apps').document(app_id).update(app_data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@apps_bp.route('/<app_id>', methods=['DELETE'])
@admin_required
def delete_app(telegram_user, app_id):
    try:
        firebase_db.collection('apps').document(app_id).delete()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500