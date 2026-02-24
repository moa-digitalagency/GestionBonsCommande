# /* * Nom de l'application : BTP Commande
#  * Description : Gestion des chantiers
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from models import db
from models.project import Project
from services.i18n_service import i18n
from security.decorators import tenant_required, admin_required
from services.tenant_service import TenantService

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
@tenant_required
def index():
    projects = TenantService.get_tenant_projects().order_by(Project.name).all()
    return render_template('projects/index.html', projects=projects)

@projects_bp.route('/add', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        description = request.form.get('description', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        contact_name = request.form.get('contact_name', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        
        if not name:
            flash(i18n.translate('Le nom du chantier est obligatoire.'), 'danger')
            return render_template('projects/form.html', project=None)
        
        project = Project(
            company_id=current_user.company_id,
            name=name,
            code=code,
            description=description,
            address=address,
            city=city,
            contact_name=contact_name,
            contact_phone=contact_phone,
            is_active=True
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash(i18n.translate('Chantier créé avec succès.'), 'success')
        return redirect(url_for('projects.index'))
    
    return render_template('projects/form.html', project=None)

@projects_bp.route('/<int:project_id>')
@login_required
@tenant_required
def view(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not TenantService.validate_tenant_access(project):
        flash(i18n.translate('Accès non autorisé.'), 'danger')
        return redirect(url_for('projects.index'))
    
    orders = project.orders.order_by('created_at desc').limit(20).all()
    
    return render_template('projects/view.html', project=project, orders=orders)

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@tenant_required
@admin_required
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not TenantService.validate_tenant_access(project):
        flash(i18n.translate('Accès non autorisé.'), 'danger')
        return redirect(url_for('projects.index'))
    
    if request.method == 'POST':
        project.name = request.form.get('name', project.name).strip()
        project.code = request.form.get('code', '').strip()
        project.description = request.form.get('description', '').strip()
        project.address = request.form.get('address', '').strip()
        project.city = request.form.get('city', '').strip()
        project.contact_name = request.form.get('contact_name', '').strip()
        project.contact_phone = request.form.get('contact_phone', '').strip()
        project.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash(i18n.translate('Chantier mis à jour.'), 'success')
        return redirect(url_for('projects.view', project_id=project.id))
    
    return render_template('projects/form.html', project=project)

@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@tenant_required
@admin_required
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not TenantService.validate_tenant_access(project):
        flash(i18n.translate('Accès non autorisé.'), 'danger')
        return redirect(url_for('projects.index'))
    
    if project.orders.count() > 0:
        project.is_active = False
        db.session.commit()
        flash(i18n.translate('Chantier désactivé (il contient des commandes).'), 'warning')
    else:
        db.session.delete(project)
        db.session.commit()
        flash(i18n.translate('Chantier supprimé.'), 'success')
    
    return redirect(url_for('projects.index'))
