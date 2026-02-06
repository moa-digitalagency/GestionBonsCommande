from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    
    email = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    
    # Deprecated role string, kept for backward compatibility during migration
    role = db.Column(db.String(20), nullable=False, default='demandeur')
    preferred_language = db.Column(db.String(10), default='fr')
    avatar_color = db.Column(db.String(20), default='blue')
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    orders_created = db.relationship('Order', foreign_keys='Order.created_by_id', backref='creator', lazy='dynamic')
    orders_validated = db.relationship('Order', foreign_keys='Order.validated_by_id', backref='validator', lazy='dynamic')
    order_history = db.relationship('OrderHistory', backref='user', lazy='dynamic')
    lexique_suggestions = db.relationship('LexiqueSuggestion', foreign_keys='LexiqueSuggestion.suggested_by_id', backref='suggested_by_user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_admin(self):
        return self.role in ['super_admin', 'admin']
    
    def is_valideur(self):
        return self.role in ['super_admin', 'admin', 'valideur']
    
    def can_validate_orders(self):
        return self.role in ['super_admin', 'admin', 'valideur']
    
    def can_create_orders(self):
        return self.role in ['super_admin', 'admin', 'valideur', 'demandeur']
    
    def has_permission(self, permission_code):
        if self.role == 'super_admin':  # Legacy Super Admin check
            return True
        if self.user_role and self.user_role.name == 'Super Admin': # New RBAC Super Admin
            return True

        if self.user_role:
            for perm in self.user_role.permissions:
                if perm.code == permission_code:
                    return True
        return False

    def __repr__(self):
        return f'<User {self.email}>'
