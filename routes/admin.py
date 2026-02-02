# Nom de l'application : BTP Commande
# Description : Routes d'administration
# Produit de : MOA Digital Agency, www.myoneart.com
# Fait par : Aisance KALONJI, www.aisancekalonji.com
# Auditer par : La CyberConfiance, www.cyberconfiance.com

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from models import db
from models.company import Company
from models.user import User
from models.order import Order
from models.lexique import LexiqueSuggestion
from security.decorators import super_admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@super_admin_required
def index():
    companies = Company.query.all()
    users_count = User.query.count()
    orders_count = Order.query.count()
    pending_suggestions = LexiqueSuggestion.query.filter_by(status='pending').count()
    
    return render_template('admin/index.html', 
                         companies=companies,
                         users_count=users_count,
                         orders_count=orders_count,
                         pending_suggestions=pending_suggestions)

@admin_bp.route('/companies')
@login_required
@super_admin_required
def companies():
    companies = Company.query.order_by(Company.name).all()
    return render_template('admin/companies.html', companies=companies)

@admin_bp.route('/companies/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_company():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ice = request.form.get('ice', '').strip()
        rc = request.form.get('rc', '').strip()
        patente = request.form.get('patente', '').strip()
        if_number = request.form.get('if_number', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        bc_prefix = request.form.get('bc_prefix', 'BC').strip()
        
        if not name:
            flash('Le nom de la société est obligatoire.', 'danger')
            return render_template('admin/company_form.html', company=None)
        
        company = Company(
            name=name,
            ice=ice,
            rc=rc,
            patente=patente,
            if_number=if_number,
            address=address,
            city=city,
            phone=phone,
            email=email,
            bc_prefix=bc_prefix,
            is_active=True
        )
        
        db.session.add(company)
        db.session.commit()
        
        flash('Société créée avec succès.', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/company_form.html', company=None)

@admin_bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    if request.method == 'POST':
        company.name = request.form.get('name', company.name).strip()
        company.ice = request.form.get('ice', '').strip()
        company.rc = request.form.get('rc', '').strip()
        company.patente = request.form.get('patente', '').strip()
        company.if_number = request.form.get('if_number', '').strip()
        company.address = request.form.get('address', '').strip()
        company.city = request.form.get('city', '').strip()
        company.phone = request.form.get('phone', '').strip()
        company.email = request.form.get('email', '').strip()
        company.bc_prefix = request.form.get('bc_prefix', 'BC').strip()
        company.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Société mise à jour.', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/company_form.html', company=company)

@admin_bp.route('/users')
@login_required
@super_admin_required
def users():
    users = User.query.order_by(User.email).all()
    companies = Company.query.all()
    return render_template('admin/users.html', users=users, companies=companies)

@admin_bp.route('/users/<int:user_id>/assign', methods=['POST'])
@login_required
@super_admin_required
def assign_user(user_id):
    user = User.query.get_or_404(user_id)
    company_id = request.form.get('company_id')
    
    if company_id:
        user.company_id = int(company_id)
    else:
        user.company_id = None
    
    db.session.commit()
    flash('Utilisateur assigné.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@super_admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get('role', 'demandeur')
    
    if role in ['super_admin', 'admin', 'valideur', 'demandeur']:
        user.role = role
        db.session.commit()
        flash('Rôle modifié.', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/stats')
@login_required
@super_admin_required
def stats():
    from sqlalchemy import func
    
    orders_by_status = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()
    
    orders_by_company = db.session.query(
        Company.name, func.count(Order.id)
    ).join(Order, Company.id == Order.company_id).group_by(Company.name).all()
    
    return render_template('admin/stats.html',
                         orders_by_status=dict(orders_by_status),
                         orders_by_company=dict(orders_by_company))
