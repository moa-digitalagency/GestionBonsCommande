from tests.base_test import BaseTestCase
from flask import session

class TestLanguageSwitch(BaseTestCase):
    def test_language_switch(self):
        """Test switching languages via the /set_language route."""

        # 1. Test switching to English
        response = self.client.get('/set_language/en', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['lang'], 'en')

        # 2. Test switching to Arabic
        response = self.client.get('/set_language/ar', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['lang'], 'ar')

        # 3. Test invalid language
        response = self.client.get('/set_language/invalid_lang', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should remain 'ar' (or previous value)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['lang'], 'ar')

    def test_language_switch_redirect(self):
        """Test that the route redirects correctly."""
        response = self.client.get('/set_language/en')
        self.assertEqual(response.status_code, 302)
        # Should redirect to index/dashboard if no referrer
        self.assertIn('location', response.headers)
