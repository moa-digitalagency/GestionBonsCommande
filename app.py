from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config.settings import Config
from models import db
from models.user import User

# Services
from services.i18n_service import i18n

# Import Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.orders import orders_bp
from routes.projects import projects_bp
from routes.products import products_bp
from routes.company import company_bp
from routes.lexique import lexique_bp
from routes.settings import settings_bp
from models.settings import SiteSettings

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='statics', static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Initialize Services
    i18n.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Inject global variables for templates
    @app.context_processor
    def inject_globals():
        return {
            'supported_languages': Config.SUPPORTED_LANGUAGES
        }

    @app.context_processor
    def inject_settings():
        try:
            settings = SiteSettings.get_instance()
            return {'settings': settings}
        except Exception:
            return {'settings': None}

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(lexique_bp, url_prefix='/lexique')
    app.register_blueprint(settings_bp, url_prefix='/parametres')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
