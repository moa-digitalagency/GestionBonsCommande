from functools import wraps
from flask import redirect, url_for, flash, request, abort
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                flash('Vous n\'avez pas les permissions nécessaires.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role == 'super_admin':
            return f(*args, **kwargs)
        if not current_user.company_id:
            flash('Votre compte n\'est associé à aucune société.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role != 'super_admin':
            flash('Accès réservé aux super administrateurs.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role not in ['super_admin', 'admin']:
            flash('Accès réservé aux administrateurs.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def valideur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.can_validate_orders():
            flash('Vous n\'avez pas les droits de validation.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
