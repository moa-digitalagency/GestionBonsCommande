import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models import db
from models.company import Company
from models.user import User
from security.decorators import admin_required, tenant_required

company_bp = Blueprint('company', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@company_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def settings():
    company = Company.query.get(current_user.company_id)
    
    if not company:
        flash('Société non trouvée.', 'danger')
        return redirect(url_for('main.dashboard'))
    
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
        company.bc_footer = request.form.get('bc_footer', '').strip()
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"logo_{company.id}_{file.filename}")
                upload_path = os.path.join(current_app.root_path, 'statics', 'uploads', 'logos')
                os.makedirs(upload_path, exist_ok=True)
                filepath = os.path.join(upload_path, filename)
                file.save(filepath)
                company.logo_path = f"uploads/logos/{filename}"
        
        db.session.commit()
        flash('Paramètres de la société mis à jour.', 'success')
    
    return render_template('company/settings.html', company=company)

@company_bp.route('/users')
@login_required
@tenant_required
@admin_required
def users():
    company = Company.query.get(current_user.company_id)
    users = User.query.filter_by(company_id=current_user.company_id).all()
    return render_template('company/users.html', company=company, users=users)

@company_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def add_user():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'demandeur')
        
        if not all([email, password, first_name, last_name]):
            flash('Veuillez remplir tous les champs obligatoires.', 'danger')
            return render_template('company/user_form.html', user=None)
        
        if role not in ['admin', 'valideur', 'demandeur']:
            role = 'demandeur'
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('company/user_form.html', user=None)
        
        user = User(
            company_id=current_user.company_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Utilisateur créé avec succès.', 'success')
        return redirect(url_for('company.users'))
    
    return render_template('company/user_form.html', user=None)

@company_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.company_id != current_user.company_id and current_user.role != 'super_admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('company.users'))
    
    if request.method == 'POST':
        user.first_name = request.form.get('first_name', user.first_name).strip()
        user.last_name = request.form.get('last_name', user.last_name).strip()
        user.phone = request.form.get('phone', '').strip()
        role = request.form.get('role', user.role)
        
        if role in ['admin', 'valideur', 'demandeur']:
            user.role = role
        
        new_password = request.form.get('password', '')
        if new_password:
            user.set_password(new_password)
        
        user.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Utilisateur mis à jour.', 'success')
        return redirect(url_for('company.users'))
    
    return render_template('company/user_form.html', user=user)

@company_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@tenant_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.company_id != current_user.company_id and current_user.role != 'super_admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('company.users'))
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('company.users'))
    
    user.is_active = False
    db.session.commit()
    
    flash('Utilisateur désactivé.', 'success')
    return redirect(url_for('company.users'))
