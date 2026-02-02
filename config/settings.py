import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    SUPPORTED_LANGUAGES = ['fr', 'ar', 'darija_lat', 'en', 'es']
    DEFAULT_LANGUAGE = 'fr'
    
    BC_STATUSES = ['BROUILLON', 'SOUMIS', 'VALIDE', 'PDF_GENERE', 'PARTAGE']
    USER_ROLES = ['super_admin', 'admin', 'valideur', 'demandeur']
