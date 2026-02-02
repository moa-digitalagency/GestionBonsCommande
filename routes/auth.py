from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Veuillez remplir tous les champs.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte a été désactivé.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        
        flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not all([email, password, first_name, last_name]):
            flash('Veuillez remplir tous les champs obligatoires.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('auth/register.html')
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='demandeur',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Votre compte a été créé. Un administrateur doit vous associer à une société.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        preferred_language = request.form.get('preferred_language', 'fr')
        
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        
        if not all([first_name, last_name]):
            flash('Le prénom et le nom sont obligatoires.', 'danger')
            return render_template('auth/profile.html')
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        current_user.preferred_language = preferred_language
        
        if new_password:
            if not current_user.check_password(current_password):
                flash('Mot de passe actuel incorrect.', 'danger')
                return render_template('auth/profile.html')
            
            if len(new_password) < 6:
                flash('Le nouveau mot de passe doit contenir au moins 6 caractères.', 'danger')
                return render_template('auth/profile.html')
            
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profil mis à jour avec succès.', 'success')
    
    return render_template('auth/profile.html')
