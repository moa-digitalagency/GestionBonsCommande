from tests.base_test import BaseTestCase
from flask import url_for

class TestLandingPage(BaseTestCase):
    def test_landing_page_unauthenticated(self):
        """Test that unauthenticated users see the landing page."""
        # Logout first just in case (though setUp creates a user, it doesn't log them in)
        self.client.get('/auth/logout', follow_redirects=True)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Check for unique content in landing.html
        self.assertIn(b'G\xc3\xa9rez vos chantiers avec', response.data) # "Gérez vos chantiers avec" UTF-8 encoded
        self.assertIn(b'Commencer maintenant', response.data)

        # Check for static assets links
        self.assertIn(b'landing.css', response.data)
        self.assertIn(b'landing.js', response.data)

    def test_landing_page_redirect_authenticated(self):
        """Test that authenticated users are redirected to the dashboard."""
        # Login
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)

        # Visit root
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Should be on dashboard
        self.assertIn(b'Tableau de bord', response.data)
        # Should NOT see landing page content
        self.assertNotIn(b'G\xc3\xa9rez vos chantiers avec', response.data)
