import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
from backend.config import FIREBASE_CREDENTIALS_PATH, ALLOWED_ORIGINS

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()
cors = CORS(resources={r"/*": {"origins": ALLOWED_ORIGINS}})