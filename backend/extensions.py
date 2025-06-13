# backend/extensions.py
import firebase_admin
from firebase_admin import credentials, firestore

firebase_db = None # Глобальная переменная для клиента Firestore

def initialize_firebase(service_account_key_path):
    global firebase_db
    try:
        cred = credentials.Certificate(service_account_key_path)
        firebase_admin.initialize_app(cred)
        firebase_db = firestore.client()
        print("Firebase Admin SDK успешно инициализирован.")
    except Exception as e:
        print(f"Ошибка инициализации Firebase Admin SDK: {e}")
        # Потенциально можно вызвать ошибку или завершить работу, если Firebase критичен
        firebase_db = None # Убедитесь, что None, если инициализация не удалась

# Вызовите initialize_firebase из app.py после загрузки конфигурации