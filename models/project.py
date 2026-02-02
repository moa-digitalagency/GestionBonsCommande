from datetime import datetime
from models import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    contact_name = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = db.relationship('Order', backref='project', lazy='dynamic')
    
    def __repr__(self):
        return f'<Project {self.name}>'
