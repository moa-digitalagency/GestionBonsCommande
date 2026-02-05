# /* * Nom de l'application : BTP Commande
#  * Description : Point d'entrée de l'application
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from flask import Flask, g, request, session
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
# from flask_babel import Babel # Removed in favor of custom JSON i18n
from services.i18n_service import i18n
from config.settings import Config
from models import db

login_manager = LoginManager()
csrf = CSRFProtect()
# babel = Babel()

def create_app():
    app = Flask(__name__, 
                static_folder='statics',
                static_url_path='/static')
    
    app.config.from_object(Config)
    
    db.init_app(app)
    csrf.init_app(app)
    # babel.init_app(app, locale_selector=get_locale)
    i18n.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'
    
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.before_request
    def before_request():
        g.current_company = None
        if current_user.is_authenticated and current_user.company_id:
            from models.company import Company
            g.current_company = Company.query.get(current_user.company_id)
    
    @app.context_processor
    def utility_processor():
        return {
            'current_company': lambda: g.get('current_company'),
            'supported_languages': Config.SUPPORTED_LANGUAGES,
            'bc_statuses': Config.BC_STATUSES,
            'user_roles': Config.USER_ROLES,
        }
    
    @app.after_request
    def add_security_headers(response):
        # Cache control
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        # Security Headers
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # Add 'unsafe-eval' to script-src for Alpine.js
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com https://cdnjs.cloudflare.com https://unpkg.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data:;"

        return response
    
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.company import company_bp
    from routes.projects import projects_bp
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.lexique import lexique_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(lexique_bp, url_prefix='/lexique')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
