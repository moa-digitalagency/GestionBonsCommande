from tests.base_test import BaseTestCase
from models import db
from models.lexique import LexiqueEntry, LexiqueSuggestion
from models.user import User

class TestLexique(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry = LexiqueEntry(
            category='materiau',
            translations={'fr': 'Ciment', 'en': 'Cement'},
            is_validated=True
        )
        db.session.add(self.entry)
        db.session.commit()

        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)

    def test_search_and_suggestion_workflow(self):
        # 1. Search existing
        response = self.client.get('/lexique/search?q=Ciment')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['found'])

        # 2. Search unknown
        response = self.client.get('/lexique/search?q=Inconnu')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['found'])

        # 3. Suggest
        response = self.client.post('/lexique/suggest', data={
            'original_term': 'Inconnu',
            'translation_fr': 'Inconnu',
            'translation_en': 'Unknown',
            'category': 'general'
        }, follow_redirects=True)
        self.assertIn(b'suggestion a \xc3\xa9t\xc3\xa9 soumise', response.data)

        # 4. Create Super Admin
        super_admin = User(
            email="super@test.com",
            first_name="Super",
            last_name="Admin",
            role="super_admin"
        )
        super_admin.set_password("password")
        db.session.add(super_admin)
        db.session.commit()

        # Logout and Login as Super Admin
        self.client.get('/auth/logout', follow_redirects=True)
        self.client.post('/auth/login', data={
            'email': 'super@test.com',
            'password': 'password'
        }, follow_redirects=True)

        # 5. Approve
        suggestion = LexiqueSuggestion.query.filter_by(original_term='Inconnu').first()
        self.assertIsNotNone(suggestion)

        response = self.client.post(f'/lexique/admin/suggestion/{suggestion.id}/approve', data={
            'translation_fr': 'Inconnu',
            'translation_en': 'Unknown'
        }, follow_redirects=True)
        self.assertIn(b'Suggestion approuv\xc3\xa9e', response.data)

        # 6. Search again (should be found now)
        response = self.client.get('/lexique/search?q=Inconnu')
        self.assertTrue(response.json['found'])
