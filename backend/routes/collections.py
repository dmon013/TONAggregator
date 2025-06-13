# backend/routes/collections.py
from flask import Blueprint, jsonify
from backend.extensions import firebase_db
from backend.utils.auth import validate_telegram_data, admin_required

collections_bp = Blueprint('collections', __name__)

# --- Публичные эндпоинты ---

@collections_bp.route('/featured', methods=['GET'])
@validate_telegram_data
def get_featured_collections(telegram_user):
    """
    Возвращает несколько ключевых подборок для главного экрана.
    ID подборок (например, 'trending', 'editors_choice') задаются вручную в админке.
    """
    try:
        # Для примера, мы "захардкодили" ID подборок, которые хотим показать
        featured_ids = ['trending-this-week', 'editors-choice']
        featured_collections = []
        
        for collection_id in featured_ids:
            collection_doc = firebase_db.collection('collections').document(collection_id).get()
            if collection_doc.exists:
                collection_data = collection_doc.to_dict()
                collection_data['id'] = collection_doc.id
                
                # Получаем детали приложений из подборки
                app_ids = collection_data.get('appIds', )
                apps_in_collection = []
                if app_ids:
                    # Используем батч-запрос для эффективности
                    app_refs = [firebase_db.collection('apps').document(app_id) for app_id in app_ids]
                    app_docs = firebase_db.get_all(app_refs)
                    for doc in app_docs:
                        if doc.exists:
                            app_data = doc.to_dict()
                            app_data['id'] = doc.id
                            apps_in_collection.append(app_data)
                
                collection_data['apps'] = apps_in_collection
                featured_collections.append(collection_data)

        return jsonify(featured_collections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@collections_bp.route('/<collection_id>', methods=['GET'])
@validate_telegram_data
def get_collection_by_id(telegram_user, collection_id):
    # Этот эндпоинт почти идентичен логике внутри /featured,
    # но возвращает только одну конкретную подборку.
    # (Логика получения приложений по appIds дублируется, в реальном проекте ее можно вынести в хелпер)
    try:
        collection_doc = firebase_db.collection('collections').document(collection_id).get()
        if not collection_doc.exists:
            return jsonify({"error": "Подборка не найдена"}), 404
        
        collection_data = collection_doc.to_dict()
        collection_data['id'] = collection_doc.id
        
        app_ids = collection_data.get('appIds', )
        apps_in_collection = []
        if app_ids:
            app_refs = [firebase_db.collection('apps').document(app_id) for app_id in app_ids]
            app_docs = firebase_db.get_all(app_refs)
            for doc in app_docs:
                if doc.exists:
                    app_data = doc.to_dict()
                    app_data['id'] = doc.id
                    apps_in_collection.append(app_data)
        
        collection_data['apps'] = apps_in_collection
        return jsonify(collection_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Админ-эндпоинты ---
# (Здесь должны быть CRUD-операции для управления подборками, защищенные @admin_required)