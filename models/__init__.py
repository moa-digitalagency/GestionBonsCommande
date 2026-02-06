from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.company import Company
from models.permission import Permission
from models.role import Role
from models.user import User
from models.project import Project
from models.product import Product
from models.order import Order, OrderLine, OrderHistory
from models.lexique import LexiqueEntry, LexiqueSuggestion
from models.settings import SiteSettings
