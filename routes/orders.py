import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import current_user, login_required
from models import db
from models.order import Order, OrderLine
from models.project import Project
from models.product import Product
from security.decorators import tenant_required
from services.tenant_service import TenantService
from services.order_service import OrderService
from services.pdf_service import PDFService
from services.lexique_service import LexiqueService

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@login_required
@tenant_required
def index():
    status = request.args.get('status', '')
    project_id = request.args.get('project_id', '')
    
    orders = TenantService.get_tenant_orders()
    
    if status:
        orders = orders.filter_by(status=status)
    if project_id:
        orders = orders.filter_by(project_id=int(project_id))
    
    orders = orders.order_by(Order.created_at.desc()).all()
    projects = TenantService.get_tenant_projects().all()
    
    return render_template('orders/index.html', orders=orders, projects=projects, 
                         current_status=status, current_project=project_id)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
@tenant_required
def create():
    projects = TenantService.get_tenant_projects().all()
    products = TenantService.get_tenant_products().all()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        requested_date_str = request.form.get('requested_date', '')
        notes = request.form.get('notes', '').strip()
        supplier_name = request.form.get('supplier_name', '').strip()
        supplier_contact = request.form.get('supplier_contact', '').strip()
        supplier_phone = request.form.get('supplier_phone', '').strip()
        
        if not project_id:
            flash('Veuillez sélectionner un chantier.', 'danger')
            return render_template('orders/create.html', projects=projects, products=products)
        
        project = Project.query.get(project_id)
        if not project or not TenantService.validate_tenant_access(project):
            flash('Chantier non valide.', 'danger')
            return render_template('orders/create.html', projects=projects, products=products)
        
        requested_date = None
        if requested_date_str:
            try:
                requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        try:
            order = OrderService.create_order(
                project_id=int(project_id),
                requested_date=requested_date,
                notes=notes,
                supplier_name=supplier_name,
                supplier_contact=supplier_contact,
                supplier_phone=supplier_phone
            )
            
            flash(f'Bon de commande {order.bc_number} créé.', 'success')
            return redirect(url_for('orders.edit', order_id=order.id))
        except Exception as e:
            flash(f'Erreur lors de la création: {str(e)}', 'danger')
    
    return render_template('orders/create.html', projects=projects, products=products)

@orders_bp.route('/<int:order_id>')
@login_required
@tenant_required
def view(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    lines = order.lines.order_by(OrderLine.line_number).all()
    history = order.history.order_by('created_at desc').all()
    
    return render_template('orders/view.html', order=order, lines=lines, history=history)

@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
@tenant_required
def edit(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    if not order.can_edit(current_user):
        flash('Vous ne pouvez pas modifier ce bon de commande.', 'warning')
        return redirect(url_for('orders.view', order_id=order.id))
    
    products = TenantService.get_tenant_products().all()
    lines = order.lines.order_by(OrderLine.line_number).all()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'update_info':
            requested_date_str = request.form.get('requested_date', '')
            order.notes = request.form.get('notes', '').strip()
            order.supplier_name = request.form.get('supplier_name', '').strip()
            order.supplier_contact = request.form.get('supplier_contact', '').strip()
            order.supplier_phone = request.form.get('supplier_phone', '').strip()
            
            if requested_date_str:
                try:
                    order.requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            db.session.commit()
            flash('Informations mises à jour.', 'success')
        
        elif action == 'add_line':
            product_id = request.form.get('product_id')
            description = request.form.get('description', '').strip()
            quantity = request.form.get('quantity', '1')
            unit = request.form.get('unit', 'unite')
            unit_price = request.form.get('unit_price', '')
            note = request.form.get('note', '').strip()
            
            if not description:
                flash('La description est obligatoire.', 'danger')
            else:
                translation_result = LexiqueService.translate(description)
                
                try:
                    OrderService.add_line(
                        order=order,
                        description=description,
                        quantity=float(quantity),
                        unit=unit,
                        unit_price=float(unit_price) if unit_price else None,
                        product_id=int(product_id) if product_id else None,
                        note=note,
                        description_translated=translation_result['translation'],
                        translation_snapshot=translation_result
                    )
                    flash('Ligne ajoutée.', 'success')
                except Exception as e:
                    flash(f'Erreur: {str(e)}', 'danger')
        
        return redirect(url_for('orders.edit', order_id=order.id))
    
    return render_template('orders/edit.html', order=order, lines=lines, products=products)

@orders_bp.route('/<int:order_id>/line/<int:line_id>/delete', methods=['POST'])
@login_required
@tenant_required
def delete_line(order_id, line_id):
    order = Order.query.get_or_404(order_id)
    line = OrderLine.query.get_or_404(line_id)
    
    if not TenantService.validate_tenant_access(order) or line.order_id != order.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    if not order.can_edit(current_user):
        flash('Vous ne pouvez pas modifier ce bon de commande.', 'warning')
        return redirect(url_for('orders.view', order_id=order.id))
    
    OrderService.delete_line(line)
    flash('Ligne supprimée.', 'success')
    return redirect(url_for('orders.edit', order_id=order.id))

@orders_bp.route('/<int:order_id>/submit', methods=['POST'])
@login_required
@tenant_required
def submit(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    try:
        OrderService.submit_order(order)
        flash('Bon de commande soumis pour validation.', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/<int:order_id>/validate', methods=['POST'])
@login_required
@tenant_required
def validate(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    try:
        OrderService.validate_order(order)
        flash('Bon de commande validé.', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/<int:order_id>/reject', methods=['POST'])
@login_required
@tenant_required
def reject(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    reason = request.form.get('reason', '')
    
    try:
        OrderService.reject_order(order, reason)
        flash('Bon de commande rejeté.', 'info')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/<int:order_id>/pdf')
@login_required
@tenant_required
def generate_pdf(order_id):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    try:
        pdf_path = PDFService.generate_order_pdf(order)
        
        if order.status == 'VALIDE':
            OrderService.mark_pdf_generated(order, pdf_path)
        
        full_path = os.path.join(current_app.root_path, pdf_path)
        return send_file(full_path, as_attachment=True, download_name=f"{order.bc_number}.pdf")
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/<int:order_id>/share/<method>')
@login_required
@tenant_required
def share(order_id, method):
    order = Order.query.get_or_404(order_id)
    
    if not TenantService.validate_tenant_access(order):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('orders.index'))
    
    if not order.can_share():
        flash('Le bon de commande doit être validé avant le partage.', 'warning')
        return redirect(url_for('orders.view', order_id=order.id))
    
    OrderService.mark_shared(order, method)
    
    company = order.company
    project = order.project
    
    message = f"Bon de Commande {order.bc_number}\n"
    message += f"Société: {company.name}\n"
    message += f"Chantier: {project.name}\n"
    if order.requested_date:
        message += f"Date souhaitée: {order.requested_date.strftime('%d/%m/%Y')}\n"
    message += f"\nArticles:\n"
    for line in order.lines:
        message += f"- {line.description}: {line.quantity} {line.unit}\n"
    
    if method == 'whatsapp':
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return redirect(f"https://wa.me/?text={encoded_message}")
    elif method == 'email':
        import urllib.parse
        subject = urllib.parse.quote(f"Bon de Commande {order.bc_number}")
        body = urllib.parse.quote(message)
        return redirect(f"mailto:?subject={subject}&body={body}")
    
    return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/translate', methods=['POST'])
@login_required
@tenant_required
def translate_term():
    data = request.get_json()
    term = data.get('term', '')
    to_lang = data.get('to_lang', 'fr')
    
    result = LexiqueService.translate(term, to_lang=to_lang)
    return jsonify(result)
