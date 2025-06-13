# backend/routes/reviews.py
from flask import Blueprint, jsonify, request
from backend.extensions import firebase_db # Убедитесь, что firebase_db импортирован и инициализирован
from backend.utils.auth import validate_telegram_data
from firebase_admin import firestore # Для firestore.Query и firestore.transactional
import datetime

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/app/<app_id>', methods=['GET'])
@validate_telegram_data
def get_reviews_for_app(telegram_user, app_id):
    try:
        reviews_ref = firebase_db.collection('reviews').where('app_id', '==', app_id).order_by('created_at', direction=firestore.Query.DESCENDING)
        reviews_list = []
        for doc in reviews_ref.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            reviews_list.append(review_data)
        return jsonify(reviews_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/', methods=['POST'])
@validate_telegram_data
def submit_review(telegram_user):
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        rating = data.get('rating')
        comment = data.get('comment')

        if not app_id or rating is None:
            return jsonify({"error": "app_id и rating обязательны"}), 400
        if not 1 <= int(rating) <= 5:
            return jsonify({"error": "Рейтинг должен быть от 1 до 5"}), 400

        # Проверка существования приложения
        app_ref = firebase_db.collection('apps').document(app_id)
        if not app_ref.get().exists:
            return jsonify({"error": "Приложение не найдено"}), 404

        review_data = {
            "app_id": app_id,
            "user_id": str(telegram_user.get('id')), # из validate_telegram_data
            "user_name": telegram_user.get('first_name', 'Аноним'),
            "rating": int(rating),
            "comment": comment,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z" # Firestore timestamp или ISO строка
        }
        
        # Добавление отзыва
        # add() возвращает кортеж (timestamp, document_reference)
        _, new_review_ref = firebase_db.collection('reviews').add(review_data)


        # ВАЖНО: Обновить средний рейтинг и количество отзывов приложения (рекомендуется транзакция)
        @firestore.transactional
        def update_app_rating_transactional(transaction, app_doc_ref_param, rating_param):
            snapshot = app_doc_ref_param.get(transaction=transaction)
            if not snapshot.exists:
                raise Exception("Приложение не найдено во время транзакции")

            app_data = snapshot.to_dict()
            current_total_rating = app_data.get('avg_rating', 0.0) * app_data.get('review_count', 0)
            new_review_count = app_data.get('review_count', 0) + 1
            new_total_rating = current_total_rating + int(rating_param)
            new_avg_rating = new_total_rating / new_review_count if new_review_count > 0 else 0

            transaction.update(app_doc_ref_param, {
                'avg_rating': round(new_avg_rating, 2),
                'review_count': new_review_count
            })

        transaction_obj = firebase_db.transaction() # Создаем объект транзакции
        update_app_rating_transactional(transaction_obj, app_ref, rating) # Передаем rating
        
        # Получаем данные добавленного отзыва для ответа
        created_review_doc = new_review_ref.get() # new_review_ref это DocumentReference
        response_data = created_review_doc.to_dict()
        response_data['id'] = created_review_doc.id
        
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/user/me', methods=['GET'])
@validate_telegram_data
def get_my_reviews(telegram_user):
    user_id = str(telegram_user.get('id'))
    try:
        reviews_ref = firebase_db.collection('reviews').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
        reviews_list = []
        for doc in reviews_ref.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            reviews_list.append(review_data)
        return jsonify(reviews_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500