from tests.base_test import BaseTestCase
from models import db
from models.project import Project
from models.product import Product
from models.order import Order
from unittest.mock import patch
import os

class TestWorkflow(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.project = Project(name="Project A", company_id=self.company.id)
        db.session.add(self.project)
        self.product = Product(reference="Prod 1", company_id=self.company.id)
        db.session.add(self.product)
        db.session.commit()

        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)

    def test_full_workflow(self):
        # 1. Create Order
        response = self.client.post('/orders/create', data={
            'project_id': self.project.id,
            'notes': 'Test Order'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        order = Order.query.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'BROUILLON')

        # 2. Add Line
        response = self.client.post(f'/orders/{order.id}/edit', data={
            'action': 'add_line',
            'product_id': self.product.id,
            'description': 'Test Item',
            'quantity': 10,
            'unit': 'unite'
        }, follow_redirects=True)
        self.assertIn(b'Ligne ajout\xc3\xa9e', response.data)

        # 3. Submit
        response = self.client.post(f'/orders/{order.id}/submit', follow_redirects=True)
        self.assertIn(b'Bon de commande soumis', response.data)

        # Refresh order
        db.session.expire(order) # Force reload
        order = Order.query.get(order.id)
        self.assertEqual(order.status, 'SOUMIS')

        # 4. Try PDF Generation (Should fail)
        response = self.client.get(f'/orders/{order.id}/pdf', follow_redirects=True)
        self.assertIn(b'Le BC doit \xc3\xaatre valid\xc3\xa9', response.data)

        # 5. Validate
        response = self.client.post(f'/orders/{order.id}/validate', follow_redirects=True)
        self.assertIn(b'Bon de commande valid\xc3\xa9', response.data)

        db.session.expire(order)
        order = Order.query.get(order.id)
        self.assertEqual(order.status, 'VALIDE')

        # 6. Generate PDF (Mocked)
        with patch('services.pdf_service.PDFService.generate_order_pdf') as mock_pdf:
            # We must make sure the file exists because the route calls send_file on the result
            dummy_rel_path = 'statics/uploads/pdfs/dummy.pdf'
            dummy_abs_path = os.path.join(self.app.root_path, dummy_rel_path)

            os.makedirs(os.path.dirname(dummy_abs_path), exist_ok=True)
            with open(dummy_abs_path, 'w') as f:
                f.write('dummy pdf content')

            mock_pdf.return_value = dummy_rel_path

            response = self.client.get(f'/orders/{order.id}/pdf')
            self.assertEqual(response.status_code, 200)

            # Verify Status Update
            db.session.expire(order)
            order = Order.query.get(order.id)
            self.assertEqual(order.status, 'PDF_GENERE')
