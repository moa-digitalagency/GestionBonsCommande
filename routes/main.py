from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import current_user, login_required
from urllib.parse import urlparse, urljoin
from config.settings import Config

main_bp = Blueprint('main', __name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@main_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in Config.SUPPORTED_LANGUAGES:
        session['lang'] = lang_code

    referrer = request.referrer
    if referrer and is_safe_url(referrer):
        return redirect(referrer)
    return redirect(url_for('main.index'))

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from models.order import Order
    from models.project import Project
    from models.product import Product
    from services.tenant_service import TenantService
    
    if current_user.role == 'super_admin':
        from models.company import Company
        from models.lexique import LexiqueSuggestion
        companies = Company.query.filter_by(is_active=True).all()
        pending_suggestions = LexiqueSuggestion.query.filter_by(status='pending').count()
        return render_template('dashboard_admin.html', 
                             companies=companies,
                             pending_suggestions=pending_suggestions)
    
    orders = TenantService.get_tenant_orders().order_by(Order.created_at.desc()).limit(10).all()
    projects = TenantService.get_tenant_projects().all()
    products = TenantService.get_tenant_products().count()
    
    pending_orders = TenantService.get_tenant_orders().filter_by(status='SOUMIS').count()
    
    return render_template('dashboard.html',
                         orders=orders,
                         projects=projects,
                         products_count=products,
                         pending_orders=pending_orders)
