from tests.base_test import BaseTestCase
from models import db
from models.company import Company
from models.user import User
from models.project import Project
from models.order import Order

class TestTenantIsolation(BaseTestCase):
    def setUp(self):
        super().setUp()

        # Setup Company A Assets (User A is self.user, Company A is self.company)
        self.project_a = Project(name="Project A", company_id=self.company.id)
        db.session.add(self.project_a)
        db.session.commit()

        # Setup Company B
        self.company_b = Company(name="Company B", ice="987654321")
        db.session.add(self.company_b)
        db.session.commit()

        # Setup User B
        self.user_b = User(
            email="userb@test.com",
            first_name="User",
            last_name="B",
            company_id=self.company_b.id,
            role="admin"
        )
        self.user_b.set_password("password")
        db.session.add(self.user_b)
        db.session.commit()

    def test_order_isolation(self):
        # 1. Login as User A and create an order
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)

        # Create order manually in DB to save HTTP calls, but linked to Company A
        order_a = Order(
            company_id=self.company.id,
            project_id=self.project_a.id,
            bc_number="BC-TEST-001",
            status="BROUILLON",
            created_by_id=self.user.id
        )
        db.session.add(order_a)
        db.session.commit()

        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BC-TEST-001', response.data)

        self.client.get('/auth/logout', follow_redirects=True)

        # 2. Login as User B
        self.client.post('/auth/login', data={
            'email': 'userb@test.com',
            'password': 'password'
        }, follow_redirects=True)

        # 3. Check list
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'BC-TEST-001', response.data)

        # 4. Try to access Order A directly
        response = self.client.get(f'/orders/{order_a.id}', follow_redirects=True)
        # Should redirect to index with flash message "Accès non autorisé"
        self.assertIn(b'Acc\xc3\xa8s non autoris\xc3\xa9', response.data)
