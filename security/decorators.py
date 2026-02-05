from functools import wraps
from services.i18n_service import i18n
from flask import redirect, url_for, flash, request, abort
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                flash(i18n.translate('Vous n\'avez pas les permissions nécessaires.'), 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role == 'super_admin':
            return f(*args, **kwargs)
        if not current_user.company_id:
            flash(i18n.translate('Votre compte n\'est associé à aucune société.'), 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role != 'super_admin':
            flash(i18n.translate('Accès réservé aux super administrateurs.'), 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role not in ['super_admin', 'admin']:
            flash(i18n.translate('Accès réservé aux administrateurs.'), 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def valideur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(i18n.translate('Veuillez vous connecter pour accéder à cette page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.can_validate_orders():
            flash(i18n.translate('Vous n\'avez pas les droits de validation.'), 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
