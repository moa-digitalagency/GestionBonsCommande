# /* * Nom de l'application : BTP Commande
#  * Description : Administration et gestion des utilisateurs
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from models import db
from models.company import Company
from services.i18n_service import i18n
from models.user import User
from models.role import Role
from models.permission import Permission
from models.order import Order
from models.lexique import LexiqueSuggestion
from security.decorators import super_admin_required, permission_required

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/')
@login_required
def index():
    # Basic check: user must have some admin privs
    if not (current_user.has_permission('manage_users') or current_user.has_permission('manage_roles') or current_user.has_permission('manage_dictionary')):
         flash(i18n.translate('Accès non autorisé.'), 'danger')
         return redirect(url_for('main.dashboard'))

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
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        bc_prefix = request.form.get('bc_prefix', 'BC').strip()
        
        if not name:
            flash(i18n.translate('Le nom de la société est obligatoire.'), 'danger')
            return render_template('admin/company_form.html', company=None)
        
        company = Company(
            name=name,
            ice=ice,
            rc=rc,
            address=address,
            city=city,
            phone=phone,
            email=email,
            bc_prefix=bc_prefix,
            is_active=True
        )
        
        db.session.add(company)
        db.session.commit()

        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"company_{company.id}_{file.filename}")
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                company.logo_path = f"uploads/companies/{filename}"
                db.session.commit()
        
        flash(i18n.translate('Société créée avec succès.'), 'success')
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
        company.address = request.form.get('address', '').strip()
        company.city = request.form.get('city', '').strip()
        company.phone = request.form.get('phone', '').strip()
        company.email = request.form.get('email', '').strip()
        company.bc_prefix = request.form.get('bc_prefix', 'BC').strip()
        company.is_active = request.form.get('is_active') == 'on'

        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"company_{company.id}_{file.filename}")
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                company.logo_path = f"uploads/companies/{filename}"
        
        db.session.commit()
        flash(i18n.translate('Société mise à jour.'), 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/company_form.html', company=company)

# --- USERS MANAGEMENT ---

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def users():
    if request.method == 'POST':
        # Create User
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '').strip()
        role_id = request.form.get('role_id')
        company_id = request.form.get('company_id')

        if not email or not first_name or not last_name or not password:
            flash(i18n.translate('Tous les champs obligatoires doivent être remplis.'), 'danger')
        elif User.query.filter_by(email=email).first():
            flash(i18n.translate('Cet email est déjà utilisé.'), 'danger')
        else:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=role_id if role_id else None,
                company_id=company_id if company_id else None,
                is_active=True
            )
            user.set_password(password)

            # Sync legacy role field for backward compatibility
            if role_id:
                role = Role.query.get(role_id)
                if role and role.name == 'Super Admin':
                    user.role = 'super_admin'
                else:
                    user.role = 'demandeur' # Default fallback

            db.session.add(user)
            db.session.commit()
            flash(i18n.translate('Utilisateur créé avec succès.'), 'success')
            return redirect(url_for('admin.users'))

    users = User.query.order_by(User.email).all()
    roles = Role.query.all()
    companies = Company.query.all()
    return render_template('admin/users.html', users=users, roles=roles, companies=companies)

@admin_bp.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@permission_required('manage_users')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Update Role
    role_id = request.form.get('role_id')
    if role_id:
        user.role_id = int(role_id)
        # Sync legacy
        role = Role.query.get(role_id)
        if role and role.name == 'Super Admin':
            user.role = 'super_admin'
        else:
            user.role = 'demandeur'

    # Update Company
    company_id = request.form.get('company_id')
    if company_id:
        user.company_id = int(company_id)
    else:
        user.company_id = None

    db.session.commit()
    flash(i18n.translate('Utilisateur mis à jour.'), 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@permission_required('manage_users')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash(i18n.translate('Vous ne pouvez pas vous désactiver vous-même.'), 'warning')
        return redirect(url_for('admin.users'))

    user.is_active = False
    db.session.commit()
    flash(i18n.translate('Utilisateur désactivé.'), 'success')
    return redirect(url_for('admin.users'))

# --- ROLES MANAGEMENT ---

@admin_bp.route('/roles', methods=['GET', 'POST'])
@login_required
@permission_required('manage_roles')
def roles():
    if request.method == 'POST':
        # Create or Update Role
        role_id = request.form.get('role_id')
        name = request.form.get('name', '').strip()
        color = request.form.get('color', 'blue')
        permission_ids = request.form.getlist('permissions')

        if not name:
             flash(i18n.translate('Le nom du rôle est obligatoire.'), 'danger')
             return redirect(url_for('admin.roles'))

        if role_id:
            role = Role.query.get_or_404(role_id)
            role.name = name
            role.color = color
            flash(i18n.translate('Rôle mis à jour.'), 'success')
        else:
            role = Role(name=name, color=color)
            db.session.add(role)
            flash(i18n.translate('Rôle créé.'), 'success')

        # Update Permissions
        role.permissions = []
        for perm_id in permission_ids:
            perm = Permission.query.get(perm_id)
            if perm:
                role.permissions.append(perm)

        db.session.commit()
        return redirect(url_for('admin.roles'))

    roles = Role.query.all()
    permissions = Permission.query.all()
    # Group permissions by category (optional, for now just list)
    return render_template('admin/roles.html', roles=roles, permissions=permissions)

@admin_bp.route('/stats')
@login_required
@permission_required('view_dashboard') # Changed from super_admin_required
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
