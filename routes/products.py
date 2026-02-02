from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from models import db
from models.product import Product
from security.decorators import tenant_required, admin_required
from services.tenant_service import TenantService
from config.settings import Config

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
@tenant_required
def index():
    category = request.args.get('category', '')
    products = TenantService.get_tenant_products()
    
    if category:
        products = products.filter_by(category=category)
    
    products = products.order_by(Product.category, Product.reference).all()
    
    return render_template('products/index.html', products=products, current_category=category)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def add():
    if request.method == 'POST':
        reference = request.form.get('reference', '').strip()
        category = request.form.get('category', 'materiau')
        unit = request.form.get('unit', 'unite')
        unit_price = request.form.get('unit_price', '')
        
        labels = {}
        for lang in Config.SUPPORTED_LANGUAGES:
            label = request.form.get(f'label_{lang}', '').strip()
            if label:
                labels[lang] = label
        
        if not labels.get('fr'):
            flash('Le libellé en français est obligatoire.', 'danger')
            return render_template('products/form.html', product=None, languages=Config.SUPPORTED_LANGUAGES)
        
        product = Product(
            company_id=current_user.company_id,
            reference=reference,
            category=category,
            labels=labels,
            unit=unit,
            unit_price=float(unit_price) if unit_price else None,
            is_active=True
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Article créé avec succès.', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/form.html', product=None, languages=Config.SUPPORTED_LANGUAGES)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not TenantService.validate_tenant_access(product):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('products.index'))
    
    if request.method == 'POST':
        product.reference = request.form.get('reference', '').strip()
        product.category = request.form.get('category', 'materiau')
        product.unit = request.form.get('unit', 'unite')
        unit_price = request.form.get('unit_price', '')
        product.unit_price = float(unit_price) if unit_price else None
        
        labels = {}
        for lang in Config.SUPPORTED_LANGUAGES:
            label = request.form.get(f'label_{lang}', '').strip()
            if label:
                labels[lang] = label
        
        if not labels.get('fr'):
            flash('Le libellé en français est obligatoire.', 'danger')
            return render_template('products/form.html', product=product, languages=Config.SUPPORTED_LANGUAGES)
        
        product.labels = labels
        product.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Article mis à jour.', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/form.html', product=product, languages=Config.SUPPORTED_LANGUAGES)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
@tenant_required
@admin_required
def delete(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not TenantService.validate_tenant_access(product):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('products.index'))
    
    if product.order_lines.count() > 0:
        product.is_active = False
        db.session.commit()
        flash('Article désactivé (il est utilisé dans des commandes).', 'warning')
    else:
        db.session.delete(product)
        db.session.commit()
        flash('Article supprimé.', 'success')
    
    return redirect(url_for('products.index'))

@products_bp.route('/search')
@login_required
@tenant_required
def search():
    query = request.args.get('q', '').strip().lower()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    products = TenantService.get_tenant_products().all()
    
    results = []
    for product in products:
        match = False
        if product.reference and query in product.reference.lower():
            match = True
        for lang, label in (product.labels or {}).items():
            if label and query in label.lower():
                match = True
                break
        
        if match:
            results.append({
                'id': product.id,
                'reference': product.reference,
                'label': product.get_label('fr'),
                'unit': product.unit,
                'unit_price': float(product.unit_price) if product.unit_price else None,
                'category': product.category
            })
    
    return jsonify(results[:20])
