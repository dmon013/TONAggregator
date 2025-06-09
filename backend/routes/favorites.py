from flask import Blueprint, request, jsonify
from ..extensions import db
from ..config import FAVORITES_COLLECTION
from firebase_admin import firestore

favorites_bp = Blueprint('favorites_bp', __name__)

@favorites_bp.route('/', methods=['POST'])
def add_favorite():
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

@favorites_bp.route('/<fav_id>', methods=['DELETE'])
def delete_favorite(fav_id):
    fav_ref = db.collection(FAVORITES_COLLECTION).document(fav_id)
    fav_ref.delete()
    return jsonify({"result": "deleted"}), 200

@favorites_bp.route('/user/<user_id>', methods=['GET'])
def get_user_favorites(user_id):
    docs = db.collection(FAVORITES_COLLECTION).where('userId', '==', user_id).stream()
    favorites = [doc.to_dict()['appId'] for doc in docs]
    return jsonify(favorites), 200