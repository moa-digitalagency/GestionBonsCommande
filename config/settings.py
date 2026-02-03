# /* * Nom de l'application : BTP Commande
#  * Description : Configuration globale de l'application
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from datetime import timedelta

class Config:
    # Security: Enforce strong secret key in production
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("No SESSION_SECRET set for production configuration.")
        SECRET_KEY = 'dev-secret-key-change-in-production'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///btp_commande.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Security: Cookie settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    SUPPORTED_LANGUAGES = ['fr', 'ar', 'darija_lat', 'en', 'es']
    DEFAULT_LANGUAGE = 'fr'
    
    BC_STATUSES = ['BROUILLON', 'SOUMIS', 'VALIDE', 'PDF_GENERE', 'PARTAGE']
    USER_ROLES = ['super_admin', 'admin', 'valideur', 'demandeur']

    # Super Admin Configuration
    SUPER_ADMIN_EMAIL = os.environ.get('SUPER_ADMIN_EMAIL', 'admin@btpcommande.ma')
    SUPER_ADMIN_PASSWORD = os.environ.get('SUPER_ADMIN_PASSWORD', 'admin123')
    SUPER_ADMIN_FIRST_NAME = os.environ.get('SUPER_ADMIN_FIRST_NAME', 'Super')
    SUPER_ADMIN_LAST_NAME = os.environ.get('SUPER_ADMIN_LAST_NAME', 'Admin')
