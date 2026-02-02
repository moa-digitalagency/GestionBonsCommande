from flask import g
from flask_login import current_user
from models import db
from models.company import Company
from models.project import Project
from models.product import Product
from models.order import Order

class TenantService:
    @staticmethod
    def get_current_company():
        if hasattr(g, 'current_company'):
            return g.current_company
        
        if current_user.is_authenticated and current_user.company_id:
            company = Company.query.get(current_user.company_id)
            g.current_company = company
            return company
        return None
    
    @staticmethod
    def get_company_by_id(company_id):
        return Company.query.get(company_id)
    
    @staticmethod
    def filter_by_tenant(query, model):
        if current_user.is_authenticated:
            if current_user.role == 'super_admin':
                return query
            if current_user.company_id:
                return query.filter(model.company_id == current_user.company_id)
        return query.filter(False)
    
    @staticmethod
    def get_tenant_projects():
        if not current_user.is_authenticated:
            return Project.query.filter(False)
        
        if current_user.role == 'super_admin':
            return Project.query
        
        if current_user.company_id:
            return Project.query.filter_by(company_id=current_user.company_id, is_active=True)
        
        return Project.query.filter(False)
    
    @staticmethod
    def get_tenant_products():
        if not current_user.is_authenticated:
            return Product.query.filter(False)
        
        if current_user.role == 'super_admin':
            return Product.query
        
        if current_user.company_id:
            return Product.query.filter_by(company_id=current_user.company_id, is_active=True)
        
        return Product.query.filter(False)
    
    @staticmethod
    def get_tenant_orders():
        if not current_user.is_authenticated:
            return Order.query.filter(False)
        
        if current_user.role == 'super_admin':
            return Order.query
        
        if current_user.company_id:
            return Order.query.filter_by(company_id=current_user.company_id)
        
        return Order.query.filter(False)
    
    @staticmethod
    def validate_tenant_access(obj):
        if not current_user.is_authenticated:
            return False
        
        if current_user.role == 'super_admin':
            return True
        
        if hasattr(obj, 'company_id'):
            return obj.company_id == current_user.company_id
        
        return False
