from datetime import datetime
from flask_login import current_user
from models import db
from models.company import Company
from models.order import Order, OrderLine, OrderHistory

class OrderService:
    @staticmethod
    def create_order(project_id, requested_date=None, notes=None,
                     notes_internal=None, notes_supplier_fr=None, notes_supplier_en=None,
                     supplier_name=None, supplier_contact=None, supplier_phone=None):
        company = Company.query.get(current_user.company_id)
        if not company:
            raise ValueError("Société non trouvée")
        
        # New Numbering Engine Logic
        bc_number = OrderService.generate_reference(company)
        
        order = Order(
            company_id=current_user.company_id,
            project_id=project_id,
            bc_number=bc_number,
            status='BROUILLON',
            requested_date=requested_date,
            notes=notes,
            notes_internal=notes_internal,
            notes_supplier_fr=notes_supplier_fr,
            notes_supplier_en=notes_supplier_en,
            supplier_name=supplier_name,
            supplier_contact=supplier_contact,
            supplier_phone=supplier_phone,
            created_by_id=current_user.id
        )
        
        db.session.add(order)
        db.session.commit()
        
        OrderService.add_history(order, 'CREATION', None, 'BROUILLON', 
                                 {'message': 'Création du bon de commande'})
        
        return order
    
    @staticmethod
    def generate_reference(company):
        # Default fallback
        prefix = 'BC'
        separator = '-'
        year_format = 'YYYY'
        length = 3
        start_number = 1

        if company.settings and 'numbering' in company.settings:
            n = company.settings['numbering']
            prefix = n.get('prefix', 'BC')
            separator = n.get('separator', '-')
            year_format = n.get('year_format', 'YYYY')
            length = int(n.get('sequence_length', 3))
            start_number = int(n.get('start_number', 1))

        # Manage counter
        # We use bc_counter from company model as the persistent counter
        # Check if we need to jump to start_number
        if company.bc_counter < start_number - 1:
            company.bc_counter = start_number - 1

        company.bc_counter += 1
        seq_num = company.bc_counter

        now = datetime.utcnow()
        year_str = str(now.year) if year_format == 'YYYY' else str(now.year)[2:]
        seq_str = str(seq_num).zfill(length)

        return f"{prefix}{separator}{year_str}{separator}{seq_str}"

    @staticmethod
    def add_line(order, description, quantity, unit='unite', unit_price=None, 
                 product_id=None, note=None, description_translated=None, translation_snapshot=None):
        line_number = order.lines.count() + 1
        
        line = OrderLine(
            order_id=order.id,
            product_id=product_id,
            line_number=line_number,
            description=description,
            description_translated=description_translated,
            translation_snapshot=translation_snapshot,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            note=note
        )
        
        db.session.add(line)
        db.session.commit()
        
        return line
    
    @staticmethod
    def update_line(line, description=None, quantity=None, unit=None, unit_price=None, note=None):
        if description is not None:
            line.description = description
        if quantity is not None:
            line.quantity = quantity
        if unit is not None:
            line.unit = unit
        if unit_price is not None:
            line.unit_price = unit_price
        if note is not None:
            line.note = note
        
        db.session.commit()
        return line
    
    @staticmethod
    def delete_line(line):
        order = line.order
        line_number = line.line_number
        
        db.session.delete(line)
        
        for remaining_line in order.lines.filter(OrderLine.line_number > line_number).all():
            remaining_line.line_number -= 1
        
        db.session.commit()
    
    @staticmethod
    def submit_order(order):
        if order.status != 'BROUILLON':
            raise ValueError("Seul un brouillon peut être soumis")
        
        if order.lines.count() == 0:
            raise ValueError("Le bon de commande doit contenir au moins une ligne")
        
        old_status = order.status
        order.status = 'SOUMIS'
        db.session.commit()
        
        OrderService.add_history(order, 'SOUMISSION', old_status, 'SOUMIS',
                                 {'message': 'Soumission pour validation'})
        
        return order
    
    @staticmethod
    def validate_order(order):
        if order.status != 'SOUMIS':
            raise ValueError("Seul un BC soumis peut être validé")
        
        if not current_user.can_validate_orders():
            raise ValueError("Vous n'avez pas les droits pour valider")
        
        old_status = order.status
        order.status = 'VALIDE'
        order.validated_by_id = current_user.id
        order.validated_at = datetime.utcnow()
        db.session.commit()
        
        OrderService.add_history(order, 'VALIDATION', old_status, 'VALIDE',
                                 {'message': 'Validation du bon de commande'})
        
        return order
    
    @staticmethod
    def reject_order(order, reason=None):
        if order.status != 'SOUMIS':
            raise ValueError("Seul un BC soumis peut être rejeté")
        
        old_status = order.status
        order.status = 'BROUILLON'
        db.session.commit()
        
        OrderService.add_history(order, 'REJET', old_status, 'BROUILLON',
                                 {'message': 'Rejet du bon de commande', 'reason': reason})
        
        return order
    
    @staticmethod
    def mark_pdf_generated(order, pdf_path):
        if order.status != 'VALIDE':
            raise ValueError("Seul un BC validé peut générer un PDF")
        
        old_status = order.status
        order.status = 'PDF_GENERE'
        order.pdf_path = pdf_path
        order.pdf_generated_at = datetime.utcnow()
        db.session.commit()
        
        OrderService.add_history(order, 'PDF_GENERATION', old_status, 'PDF_GENERE',
                                 {'message': 'Génération du PDF', 'pdf_path': pdf_path})
        
        return order
    
    @staticmethod
    def mark_shared(order, share_method):
        if order.status not in ['VALIDE', 'PDF_GENERE', 'PARTAGE']:
            raise ValueError("Le BC doit être validé avant le partage")
        
        old_status = order.status
        order.status = 'PARTAGE'
        order.shared_at = datetime.utcnow()
        order.share_method = share_method
        db.session.commit()
        
        OrderService.add_history(order, 'PARTAGE', old_status, 'PARTAGE',
                                 {'message': f'Partage via {share_method}'})
        
        return order
    
    @staticmethod
    def add_history(order, action, old_status, new_status, details=None):
        history = OrderHistory(
            order_id=order.id,
            user_id=current_user.id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            details=details
        )
        db.session.add(history)
        db.session.commit()
        return history
