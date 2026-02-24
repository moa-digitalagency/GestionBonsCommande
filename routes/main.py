# /* * Nom de l'application : BTP Commande
#  * Description : Routes principales et tableau de bord
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

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
    return render_template('landing.html')

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
    
    orders_query = TenantService.get_tenant_orders()
    orders = orders_query.order_by(Order.created_at.desc()).limit(10).all()
    projects = TenantService.get_tenant_projects().all()
    
    pending_orders = orders_query.filter_by(status='SOUMIS').count()

    stats = {
        'orders_count': orders_query.count(),
        'pending_count': pending_orders,
        'projects_count': len(projects)
    }

    # Restoring products_count for backward compatibility/unused variable safety
    products_count = TenantService.get_tenant_products().count()
    
    return render_template('dashboard.html',
                         orders=orders,
                         projects=projects,
                         products_count=products_count,
                         stats=stats)
