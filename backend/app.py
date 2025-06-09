import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from flask import Flask
from backend.extensions import db, cors
from backend.routes.applications import applications_bp
from backend.routes.favorites import favorites_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    #db.init_app(app)
    cors.init_app(app)
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(favorites_bp, url_prefix='/favorites')
    # Если будут еще модули, подключай так же

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)