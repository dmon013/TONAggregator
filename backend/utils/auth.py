# backend/utils/auth.py
import hashlib
import hmac
import json
from functools import wraps
from urllib.parse import unquote
from flask import request, jsonify, current_app

def validate_telegram_data_str(init_data_str: str, bot_token: str) -> dict | None:
    """
    Проверяет строку initData из Telegram Web App.
    Возвращает данные пользователя в виде словаря, если они действительны, иначе None.
    """
    try:
        params = {}
        # Разбор строки запроса initData
        # Пример: query_id=XXX&user={"id":123...}&auth_date=XXX&hash=XXX
        for pair in init_data_str.split('&'):
            key_value = pair.split('=', 1)
            if len(key_value) == 2:
                 params[key_value] = unquote(key_value[1]) # Декодируем URL-кодированные значения
            else: 
                 params[key_value] = ""


        if 'hash' not in params:
            current_app.logger.warning("Параметр 'hash' отсутствует в initData.")
            return None

        received_hash = params.pop('hash') # Извлекаем хеш для проверки, удаляя его из params
        
        # Формируем data_check_string: все пары ключ=значение, отсортированные по ключу, объединенные через '\n'
        data_check_string_parts = []
        for key, value in sorted(params.items()): # Сортируем по ключу
            data_check_string_parts.append(f"{key}={value}")
        
        data_check_string = "\n".join(data_check_string_parts)

        # Вычисляем хеш на нашей стороне
        # 1. Секретный ключ генерируется как HMAC-SHA256 от токена бота с ключом "WebAppData"
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        # 2. Итоговый хеш - это HMAC-SHA256 от data_check_string с использованием сгенерированного секретного ключа
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash == received_hash:
            # Хеши совпадают, данные действительны
            user_data_str = params.get('user')
            if user_data_str:
                try:
                    # Поле 'user' обычно является JSON-строкой, ее нужно распарсить
                    return json.loads(user_data_str) 
                except json.JSONDecodeError:
                    current_app.logger.error(f"Ошибка декодирования JSON для пользователя: {user_data_str}")
                    return None 
            # Если поля 'user' нет, но хеш валиден (маловероятно для стандартного initData),
            # можно вернуть все параметры, но это не стандартный случай для идентификации пользователя.
            # Для нашего магазина приложений, нам нужен объект user.
            current_app.logger.warning("initData валиден, но поле 'user' отсутствует или не является JSON.")
            return None # Или params, если это допустимо для вашего случая
        else:
            current_app.logger.warning(f"Несовпадение хешей. Полученный: {received_hash}, Вычисленный: {calculated_hash}")
            return None
    except Exception as e:
        current_app.logger.error(f"Исключение при валидации данных Telegram: {e}")
        return None

def validate_telegram_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # Ожидаем заголовок в формате "TmaInitData <строка_initData>"
        if not auth_header or not auth_header.startswith('TmaInitData '):
            return jsonify({"error": "Отсутствует или неверный заголовок Authorization"}), 401
        
        init_data_str = auth_header.split(' ', 1)[1] # Извлекаем саму строку initData
        
        # Получаем токен бота из конфигурации приложения Flask
        bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            current_app.logger.error("TELEGRAM_BOT_TOKEN не настроен на бэкенде.")
            return jsonify({"error": "Ошибка конфигурации сервера"}), 500

        # Валидируем initData
        user_info = validate_telegram_data_str(init_data_str, bot_token)

        if not user_info or 'id' not in user_info: # Убеждаемся, что получили информацию о пользователе с ID
            return jsonify({"error": "Неверные или неавторизованные данные Telegram"}), 403
        
        # Если валидация прошла успешно, внедряем информацию о пользователе (user_info)
        # в аргументы вызываемой функции маршрута.
        return f(telegram_user=user_info, *args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @validate_telegram_data # Сначала проверяем, что пользователь валиден
    def decorated_function(telegram_user, *args, **kwargs):
        user_id = str(telegram_user.get('id'))
        
        # Проверяем роль пользователя в Firestore
        try:
            user_doc = firebase_db.collection('users').document(user_id).get()
            if user_doc.exists and user_doc.to_dict().get('role') == 'admin':
                # Если роль 'admin', выполняем защищенную функцию
                return f(telegram_user, *args, **kwargs)
            else:
                # В противном случае - доступ запрещен
                return jsonify({"error": "Admin access required"}), 403
        except Exception as e:
            return jsonify({"error": "Failed to verify admin role", "details": str(e)}), 500
            
    return decorated_function