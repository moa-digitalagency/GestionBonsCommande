from datetime import datetime
from models import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    logo_path = db.Column(db.String(500), nullable=True)
    
    ice = db.Column(db.String(50), nullable=True)
    rc = db.Column(db.String(50), nullable=True)
    patente = db.Column(db.String(50), nullable=True)
    if_number = db.Column(db.String(50), nullable=True)
    
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    
    bc_prefix = db.Column(db.String(20), default='BC')
    bc_counter = db.Column(db.Integer, default=0)
    bc_footer = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', backref='company', lazy='dynamic')
    projects = db.relationship('Project', backref='company', lazy='dynamic')
    products = db.relationship('Product', backref='company', lazy='dynamic')
    orders = db.relationship('Order', backref='company', lazy='dynamic')
    
    def generate_bc_number(self):
        self.bc_counter += 1
        year = datetime.utcnow().year
        return f"{self.bc_prefix}-{year}-{str(self.bc_counter).zfill(4)}"
    
    def __repr__(self):
        return f'<Company {self.name}>'
