from datetime import datetime
from models import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    reference = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='materiau')
    
    labels = db.Column(db.JSON, nullable=False, default=dict)
    
    unit = db.Column(db.String(20), nullable=False, default='unite')
    unit_price = db.Column(db.Numeric(12, 2), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order_lines = db.relationship('OrderLine', backref='product', lazy='dynamic')
    
    def get_label(self, lang='fr'):
        if self.labels and lang in self.labels:
            return self.labels[lang]
        if self.labels and 'fr' in self.labels:
            return self.labels['fr']
        return self.reference or f"Product #{self.id}"
    
    def set_label(self, lang, value):
        if not self.labels:
            self.labels = {}
        self.labels[lang] = value
    
    def __repr__(self):
        return f'<Product {self.reference}>'
