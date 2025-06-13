# seed_firestore.py
import firebase_admin
from firebase_admin import credentials, firestore

# --- Настройка ---
SERVICE_ACCOUNT_KEY_PATH = 'serviceAccountKey.json'
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase Admin SDK успешно инициализирован.")
except Exception as e:
    print(f"✗ Ошибка инициализации Firebase: {e}")
    exit()

def seed_data():
    """Основная функция для заполнения базы данных."""
    print("🔥 Очистка коллекций...")
    collections_to_delete = ['apps', 'categories', 'collections', 'users', 'news']
    for coll in collections_to_delete:
        docs = db.collection(coll).stream()
        for doc in docs:
            doc.reference.delete()
    print("✓ Коллекции очищены.")

    batch = db.batch()
    
    # --- 1. Создание Категорий ---
    print("⏳ Создание категорий...")
    categories = {
        "games": {"name": "Игры", "iconUrl": "..."},
        "utils": {"name": "Утилиты", "iconUrl": "..."},
        "finance": {"name": "Финансы", "iconUrl": "..."},
    }
    category_refs = {}
    for cat_id, cat_data in categories.items():
        ref = db.collection('categories').document(cat_id)
        batch.set(ref, cat_data)
        category_refs[cat_id] = ref.id
    print(f"✓ {len(categories)} категорий добавлено.")

    # --- 2. Создание Приложений ---
    print("⏳ Создание приложений...")
    apps = {
        "app1": {"name": "Pixel Adventure", "description": "Захватывающее пиксельное приключение.", "categories": [category_refs["games"]], "iconUrl": "...", "screenshots": [], "openLink": "...", "isEditorsChoice": True, "votesCount": 120, "usageCount": 500},
        "app2": {"name": "Quick Notes", "description": "Простой блокнот.", "categories": [category_refs["utils"]], "iconUrl": "...", "screenshots": [], "openLink": "...", "isEditorsChoice": False, "votesCount": 80, "usageCount": 1500},
        "app3": {"name": "TON Tracker", "description": "Отслеживание кошельков.", "categories": [category_refs["finance"]], "iconUrl": "...", "screenshots": [], "openLink": "...", "isEditorsChoice": True, "votesCount": 250, "usageCount": 800},
        "app4": {"name": "Space Invaders", "description": "Классическая аркада.", "categories": [category_refs["games"]], "iconUrl": "...", "screenshots": [], "openLink": "...", "isEditorsChoice": False, "votesCount": 95, "usageCount": 300},
    }
    app_refs = {}
    for app_id, app_data in apps.items():
        app_data['createdAt'] = firestore.SERVER_TIMESTAMP
        ref = db.collection('apps').document(app_id)
        batch.set(ref, app_data)
        app_refs[app_id] = ref.id
    print(f"✓ {len(apps)} приложений добавлено.")

    # --- 3. Создание Подборок ---
    print("⏳ Создание подборок...")
    collections_data = {
        "trending-this-week": {"title": "Тренды Недели", "description": "Самые популярные приложения за последнюю неделю.", "appIds": [app_refs["app3"], app_refs["app1"], app_refs["app2"]]},
        "editors-choice": {"title": "Выбор Редакции", "description": "Приложения, которые мы рекомендуем.", "appIds": [app_refs["app1"], app_refs["app3"]]},
    }
    for coll_id, coll_data in collections_data.items():
        ref = db.collection('collections').document(coll_id)
        batch.set(ref, coll_data)
    print(f"✓ {len(collections_data)} подборок добавлено.")

    # --- 4. Создание Пользователей (включая админа) ---
    print("⏳ Создание пользователей...")
    users_data = {
        "123456789": {"first_name": "Admin User", "role": "admin", "recentlyOpened": [app_refs["app1"]], "votedApps": []}, # ID вашего Telegram для тестов
        "987654321": {"first_name": "Regular User", "role": "user", "recentlyOpened": [app_refs["app2"], app_refs["app4"]], "votedApps": [app_refs["app2"]]},
    }
    for user_id, user_data in users_data.items():
        ref = db.collection('users').document(user_id)
        batch.set(ref, user_data)
    print(f"✓ {len(users_data)} пользователей добавлено.")

    # --- 5. Отправка всех данных ---
    try:
        print("🚀 Отправка данных в Firestore...")
        batch.commit()
        print("✅ База данных успешно наполнена!")
    except Exception as e:
        print(f"✗ Ошибка при отправке данных: {e}")

if __name__ == "__main__":
    seed_data()