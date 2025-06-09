from flask import Blueprint, request, jsonify, Response
from backend.extensions import db, cors
from backend.config import APPLICATIONS_COLLECTION
import json
from firebase_admin import credentials, firestore
import firebase_admin

applications_bp = Blueprint('applications_bp', __name__)

try:
    cred = credentials.Certificate('D:/TONAggregator/backend/serviceAccountKey.json')
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK инициализирован успешно.")
except Exception as e:
    print(f"Ошибка инициализации Firebase Admin SDK: {e}")
    db = None # Устанавливаем db в None, чтобы избежать ошибок дальше, если инициализация не удалась

# --- Вспомогательная функция для проверки роли администратора ---
# В реальном приложении это может быть сложнее, например, с использованием Firebase Auth Custom Claims
USERS_COLLECTION = 'users'  # Замените 'users' на фактическое имя вашей коллекции пользователей

def is_admin(user_uid):
    if not db:
        return False
    try:
        user_ref = db.collection(USERS_COLLECTION).document(user_uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get('role') == 'admin'
    except Exception as e:
        print(f"Ошибка при проверке роли администратора: {e}")
    return False

@applications_bp.route('/', methods=['GET'])
def get_approved_applications():
    try:
        apps_ref = db.collection(APPLICATIONS_COLLECTION).where('status', '==', 'approved')
        docs = apps_ref.stream()
        applications = []
        for doc in docs:
            app_data = doc.to_dict()
            app_data['id'] = doc.id
            # Firestore Timestamp -> ISO string
            if 'createdAt' in app_data and hasattr(app_data['createdAt'], 'isoformat'):
                app_data['createdAt'] = app_data['createdAt'].isoformat()
            if 'updatedAt' in app_data and hasattr(app_data['updatedAt'], 'isoformat'):
                app_data['updatedAt'] = app_data['updatedAt'].isoformat()
            applications.append(app_data)
        return Response(
            json.dumps(applications, ensure_ascii=False),
            mimetype='application/json'
        ), 200
    except Exception as e:
        print(f"Ошибка при получении приложений: {e}")
        return jsonify({"error": "Не удалось получить приложения", "details": str(e)}), 50

# Получить список всех ОДОБРЕННЫХ приложений
@applications_bp.route('/applications', methods=['GET'])
def get_bar_applications():
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    try:
        apps_ref = db.collection(APPLICATIONS_COLLECTION).where('status', '==', 'approved').order_by('createdAt', direction=firestore.Query.DESCENDING)
        docs = apps_ref.stream()
        applications = []
        for doc in docs:
            app_data = doc.to_dict()
            app_data['id'] = doc.id
            # Преобразование Timestamp в строку ISO для JSON-сериализации
            if 'createdAt' in app_data and hasattr(app_data['createdAt'], 'isoformat'):
                app_data['createdAt'] = app_data['createdAt'].isoformat()
            if 'updatedAt' in app_data and hasattr(app_data['updatedAt'], 'isoformat'):
                app_data['updatedAt'] = app_data['updatedAt'].isoformat()
            applications.append(app_data)
            return Response(
                json.dumps(applications, ensure_ascii=False),
                mimetype='application/json'
            ), 200
    except Exception as e:
        print(f"Ошибка при получении одобренных приложений: {e}")
        return jsonify({"error": "Не удалось получить приложения", "details": str(e)}), 500

# Получить детали конкретного ОДОБРЕННОГО приложения по ID
@applications_bp.route('/applications/<app_id>', methods=['GET'])
def get_application_detail(app_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    try:
        app_ref = db.collection(APPLICATIONS_COLLECTION).document(app_id)
        doc = app_ref.get()
        if doc.exists:
            app_data = doc.to_dict()
            if app_data.get('status') == 'approved':
                app_data['id'] = doc.id
                if 'createdAt' in app_data and hasattr(app_data['createdAt'], 'isoformat'):
                    app_data['createdAt'] = app_data['createdAt'].isoformat()
                if 'updatedAt' in app_data and hasattr(app_data['updatedAt'], 'isoformat'):
                    app_data['updatedAt'] = app_data['updatedAt'].isoformat()
                return jsonify(app_data), 200
            else:
                return jsonify({"error": "Приложение не найдено или не одобрено"}), 404
        else:
            return jsonify({"error": "Приложение не найдено"}), 404
    except Exception as e:
        print(f"Ошибка при получении деталей приложения {app_id}: {e}")
        return jsonify({"error": "Не удалось получить детали приложения", "details": str(e)}), 500

# Пользовательская подача заявки на новое приложение
@applications_bp.route('/submit-application', methods=['POST'])
def submit_application():
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    try:
        data = request.json
        # Проверка наличия обязательных полей
        required_fields = ['title', 'category', 'description', 'appUrl', 'submittedByUserId']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Отсутствуют обязательные поля"}), 400

        # Проверка на дубликат по названию (опционально)
        existing_apps = db.collection(APPLICATIONS_COLLECTION).where('title', '==', data['title']).limit(1).stream()
        if any(existing_apps):
             return jsonify({"error": "Приложение с таким названием уже существует или ожидает рассмотрения"}), 409

        app_data = {
            "title": data['title'],
            "category": data['category'],
            "description": data['description'],
            "appUrl": data['appUrl'],
            "iconUrl": data.get('iconUrl'), # Опциональное поле
            "contact": data.get('contact'), # Опциональное поле
            "status": "pending-review",
            "submittedByUserId": data['submittedByUserId'],
            "submittedByUserEmail": data.get('submittedByUserEmail'), # Опционально
            "rating": 0, # Начальный рейтинг
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        # Добавляем новый документ с автоматически сгенерированным ID
        update_time, app_ref = db.collection(APPLICATIONS_COLLECTION).add(app_data)
        return jsonify({"message": "Заявка на приложение успешно отправлена", "appId": app_ref.id}), 201
    except Exception as e:
        print(f"Ошибка при подаче заявки: {e}")
        return jsonify({"error": "Не удалось отправить заявку", "details": str(e)}), 500

# --- Админские маршруты ---
# Для простоты, предположим, что UID администратора передается в заголовке или параметре запроса.
# В реальном приложении используйте Firebase Auth ID Token и middleware для проверки.

# (Админ) Получить список ВСЕХ приложений (включая pending)
@applications_bp.route('/admin/applications', methods=['GET'])
def admin_get_all_applications():
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    
    admin_uid = request.headers.get('X-Admin-UID') # Пример: получаем UID админа из заголовка
    if not admin_uid or not is_admin(admin_uid):
        return jsonify({"error": "Доступ запрещен: требуется авторизация администратора"}), 403
    
    try:
        apps_ref = db.collection(APPLICATIONS_COLLECTION).order_by('createdAt', direction=firestore.Query.DESCENDING)
        docs = apps_ref.stream()
        applications = []
        for doc in docs:
            app_data = doc.to_dict()
            app_data['id'] = doc.id
            if 'createdAt' in app_data and hasattr(app_data['createdAt'], 'isoformat'):
                app_data['createdAt'] = app_data['createdAt'].isoformat()
            if 'updatedAt' in app_data and hasattr(app_data['updatedAt'], 'isoformat'):
                app_data['updatedAt'] = app_data['updatedAt'].isoformat()
            applications.append(app_data)
        return jsonify(applications), 200
    except Exception as e:
        print(f"Ошибка при получении всех приложений (админ): {e}")
        return jsonify({"error": "Не удалось получить приложения", "details": str(e)}), 500

# (Админ) Добавить новое приложение напрямую (статус 'approved')
@applications_bp.route('/admin/applications', methods=['POST'])
def admin_add_application():
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500

    admin_uid = request.headers.get('X-Admin-UID')
    if not admin_uid or not is_admin(admin_uid):
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        data = request.json
        required_fields = ['title', 'category', 'description', 'appUrl', 'iconUrl', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Отсутствуют обязательные поля для добавления приложения администратором"}), 400
        
        app_data = {
            "title": data['title'],
            "category": data['category'],
            "description": data['description'],
            "appUrl": data['appUrl'],
            "iconUrl": data['iconUrl'],
            "rating": float(data.get('rating', 0)),
            "status": "approved", # Админ сразу добавляет как одобренное
            "submittedByUserId": admin_uid, # Админ является "подавшим"
            "approvedByUserId": admin_uid, # Админ является "одобрившим"
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        update_time, app_ref = db.collection(APPLICATIONS_COLLECTION).add(app_data)
        return jsonify({"message": "Приложение успешно добавлено администратором", "appId": app_ref.id}), 201
    except Exception as e:
        print(f"Ошибка при добавлении приложения администратором: {e}")
        return jsonify({"error": "Не удалось добавить приложение", "details": str(e)}), 500

# (Админ) Изменить статус приложения (одобрить/отклонить)
@applications_bp.route('/admin/applications/<app_id>/status', methods=['PUT'])
def admin_update_application_status(app_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500

    admin_uid = request.headers.get('X-Admin-UID')
    if not admin_uid or not is_admin(admin_uid):
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        data = request.json
        new_status = data.get('status')
        if new_status not in ['approved', 'rejected', 'pending-review']: # Добавил pending-review на всякий случай
            return jsonify({"error": "Недопустимый статус. Возможные значения: 'approved', 'rejected', 'pending-review'"}), 400

        app_ref = db.collection(APPLICATIONS_COLLECTION).document(app_id)
        app_doc = app_ref.get()
        if not app_doc.exists:
            return jsonify({"error": "Приложение не найдено"}), 404

        update_data = {
            "status": new_status,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        if new_status == 'approved' or new_status == 'rejected':
            update_data["approvedByUserId"] = admin_uid # Записываем, кто изменил статус

        app_ref.update(update_data)
        return jsonify({"message": f"Статус приложения {app_id} успешно изменен на {new_status}"}), 200
    except Exception as e:
        print(f"Ошибка при изменении статуса приложения {app_id}: {e}")
        return jsonify({"error": "Не удалось изменить статус приложения", "details": str(e)}), 500

# (Админ) Обновить детали приложения (опционально)
@applications_bp.route('/admin/applications/<app_id>', methods=['PUT'])
def admin_update_application_details(app_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    admin_uid = request.headers.get('X-Admin-UID')
    if not admin_uid or not is_admin(admin_uid):
        return jsonify({"error": "Доступ запрещен"}), 403
    
    try:
        data = request.json
        app_ref = db.collection(APPLICATIONS_COLLECTION).document(app_id)
        app_doc = app_ref.get()
        if not app_doc.exists:
            return jsonify({"error": "Приложение не найдено"}), 404

        # Формируем данные для обновления, только те поля, которые переданы
        update_data = {}
        allowed_fields = ['title', 'category', 'description', 'appUrl', 'iconUrl', 'rating', 'adminNotes']
        for field in allowed_fields:
            if field in data:
                if field == 'rating':
                    update_data[field] = float(data[field])
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({"error": "Нет данных для обновления"}), 400

        update_data["updatedAt"] = firestore.SERVER_TIMESTAMP
        app_ref.update(update_data)
        return jsonify({"message": f"Детали приложения {app_id} успешно обновлены"}), 200
    except Exception as e:
        print(f"Ошибка при обновлении деталей приложения {app_id}: {e}")
        return jsonify({"error": "Не удалось обновить детали", "details": str(e)}), 500


# (Админ) Удалить приложение (опционально)
@applications_bp.route('/admin/applications/<app_id>', methods=['DELETE'])
def admin_delete_application(app_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    admin_uid = request.headers.get('X-Admin-UID')
    if not admin_uid or not is_admin(admin_uid):
        return jsonify({"error": "Доступ запрещен"}), 403
    
    try:
        app_ref = db.collection(APPLICATIONS_COLLECTION).document(app_id)
        app_doc = app_ref.get()
        if not app_doc.exists:
            return jsonify({"error": "Приложение не найдено"}), 404
        
        app_ref.delete()
        return jsonify({"message": f"Приложение {app_id} успешно удалено"}), 200
    except Exception as e:
        print(f"Ошибка при удалении приложения {app_id}: {e}")
        return jsonify({"error": "Не удалось удалить приложение", "details": str(e)}), 500

# --- Маршруты для избранного ---

FAVORITES_COLLECTION = "favorites"

@applications_bp.route('/favorites', methods=['POST'])
def add_favorite():
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    data = request.json
    user_id = data.get('userId')
    app_id = data.get('appId')
    if not user_id or not app_id:
        return jsonify({"error": "userId и appId обязательны"}), 400
    fav_id = f"{user_id}_{app_id}"
    fav_ref = db.collection(FAVORITES_COLLECTION).document(fav_id)
    fav_ref.set({
        "userId": user_id,
        "appId": app_id,
        "createdAt": firestore.SERVER_TIMESTAMP
    })
    return jsonify({"id": fav_id}), 201

@applications_bp.route('/favorites/<fav_id>', methods=['DELETE'])
def delete_favorite(fav_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    fav_ref = db.collection(FAVORITES_COLLECTION).document(fav_id)
    fav_ref.delete()
    return jsonify({"result": "deleted"}), 200

@applications_bp.route('/favorites/<user_id>', methods=['GET'])
def get_user_favorites(user_id):
    if not db:
        return jsonify({"error": "База данных не инициализирована"}), 500
    docs = db.collection(FAVORITES_COLLECTION).where('userId', '==', user_id).stream()
    favorites = [doc.to_dict()['appId'] for doc in docs]
    return jsonify(favorites), 200

from flask import Flask

if __name__ == '__main__':
    # Для разработки можно использовать порт 5000 или любой другой
    # В продакшене используйте WSGI сервер, например, Gunicorn
    app = Flask(__name__)
    app.register_blueprint(applications_bp, url_prefix='/')
    app.run(debug=True, host='0.0.0.0', port=5001)