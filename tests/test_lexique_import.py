from tests.base_test import BaseTestCase
from models import db
from models.lexique import LexiqueSuggestion
from models.user import User
import pandas as pd
import io

class TestLexiqueImport(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create Super Admin
        self.super_admin = User(
            email="super@test.com",
            first_name="Super",
            last_name="Admin",
            role="super_admin"
        )
        self.super_admin.set_password("password")
        db.session.add(self.super_admin)
        db.session.commit()

        # Login as Super Admin
        self.client.post('/auth/login', data={
            'email': 'super@test.com',
            'password': 'password'
        }, follow_redirects=True)

    def test_bulk_import_csv(self):
        # Create dummy CSV
        csv_content = "fr,en,category\nBeton,Concrete,materiau\nCiment,Cement,materiau"
        data = {
            'file': (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        }

        response = self.client.post('/lexique/admin/import', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check for "termes importés" in response data
        self.assertIn(b'termes import', response.data)

        # Verify database
        suggestion = LexiqueSuggestion.query.filter_by(original_term='Beton').first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.suggested_translations['en'], 'Concrete')

    def test_bulk_import_excel(self):
        # Create dummy Excel
        df = pd.DataFrame({
            'FR': ['Brique', 'Sable'],
            'EN': ['Brick', 'Sand'],
            'Category': ['materiau', 'materiau']
        })

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        data = {
            'file': (output, 'test.xlsx')
        }

        response = self.client.post('/lexique/admin/import', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify database
        suggestion = LexiqueSuggestion.query.filter_by(original_term='Brique').first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.suggested_translations['en'], 'Brick')
