from tests.base_test import BaseTestCase
from flask import url_for, session

class TestAuth(BaseTestCase):
    def test_login_success(self):
        response = self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check if we are redirected to dashboard (Response 200 after redirect)
        # And check for dashboard content
        self.assertIn(b'Tableau de bord', response.data)

        # Verify session has user_id
        with self.client.session_transaction() as sess:
            self.assertIn('_user_id', sess)

    def test_login_failure(self):
        response = self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        # Check for the flash message
        self.assertIn(b'Email ou mot de passe incorrect', response.data)

        # Verify session does not have user_id
        with self.client.session_transaction() as sess:
            self.assertNotIn('_user_id', sess)

    def test_logout(self):
        # First login
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)

        # Then logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertIn(b'Vous avez \xc3\xa9t\xc3\xa9 d\xc3\xa9connect\xc3\xa9', response.data)

        # Verify session does not have user_id
        with self.client.session_transaction() as sess:
            self.assertNotIn('_user_id', sess)

    def test_protected_route(self):
        # Assuming /orders/ is protected
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 302) # Redirects
        self.assertTrue('/auth/login' in response.location)
