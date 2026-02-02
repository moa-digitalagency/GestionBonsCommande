import unittest
import os

# Set env vars BEFORE importing app/config so Config gets the right values
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test-secret'

from models import db
from app import create_app
from models.company import Company
from models.user import User

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Ensure it's set in app config even if Config object missed it (though import order should fix it)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create default Tenant
        self.company = Company(name="Test Company", ice="123456789")
        db.session.add(self.company)
        db.session.commit()

        # Create default User
        self.user = User(
            email="test@test.com",
            first_name="Test",
            last_name="User",
            company_id=self.company.id,
            role="admin"
        )
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
