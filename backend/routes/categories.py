# backend/routes/categories.py
from flask import Blueprint, jsonify
from backend.extensions import firebase_db
from backend.utils.auth import validate_telegram_data

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
@validate_telegram_data
def get_all_categories(telegram_user):
    try:
        categories_ref = firebase_db.collection('categories').order_by('name')
        categories_list = []
        for doc in categories_ref.stream():
            cat_data = doc.to_dict()
            cat_data['id'] = doc.id
            categories_list.append(cat_data)
        return jsonify(categories_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500