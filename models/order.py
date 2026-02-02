from datetime import datetime
from models import db
from sqlalchemy.dialects.postgresql import JSONB

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    bc_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='BROUILLON')
    
    requested_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    supplier_name = db.Column(db.String(200), nullable=True)
    supplier_contact = db.Column(db.String(200), nullable=True)
    supplier_phone = db.Column(db.String(50), nullable=True)
    
    pdf_path = db.Column(db.String(500), nullable=True)
    pdf_generated_at = db.Column(db.DateTime, nullable=True)
    
    shared_at = db.Column(db.DateTime, nullable=True)
    share_method = db.Column(db.String(50), nullable=True)
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lines = db.relationship('OrderLine', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('OrderHistory', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def can_edit(self, user):
        if self.status == 'BROUILLON':
            return user.id == self.created_by_id or user.is_admin()
        if self.status == 'SOUMIS':
            return user.can_validate_orders() and user.company_id == self.company_id
        return False
    
    def can_submit(self, user):
        return self.status == 'BROUILLON' and (user.id == self.created_by_id or user.is_admin())
    
    def can_validate(self, user):
        return self.status == 'SOUMIS' and user.can_validate_orders() and user.company_id == self.company_id
    
    def can_generate_pdf(self):
        return self.status == 'VALIDE'
    
    def can_share(self):
        return self.status in ['VALIDE', 'PDF_GENERE', 'PARTAGE']
    
    def get_total(self):
        total = 0
        for line in self.lines:
            if line.unit_price:
                total += line.quantity * float(line.unit_price)
        return total
    
    def __repr__(self):
        return f'<Order {self.bc_number}>'


class OrderLine(db.Model):
    __tablename__ = 'order_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    line_number = db.Column(db.Integer, nullable=False)
    
    description = db.Column(db.String(500), nullable=False)
    description_translated = db.Column(db.String(500), nullable=True)
    translation_snapshot = db.Column(JSONB, nullable=True)
    
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='unite')
    unit_price = db.Column(db.Numeric(12, 2), nullable=True)
    
    note = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_subtotal(self):
        if self.unit_price:
            return float(self.quantity) * float(self.unit_price)
        return 0
    
    def __repr__(self):
        return f'<OrderLine {self.line_number}: {self.description}>'


class OrderHistory(db.Model):
    __tablename__ = 'order_history'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    action = db.Column(db.String(50), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=True)
    
    details = db.Column(JSONB, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderHistory {self.action} on Order {self.order_id}>'
