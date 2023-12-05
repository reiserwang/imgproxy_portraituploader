import unittest
from app_main import app
from config import Config  # Import the Config class from config.py

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect (302) if the user is not logged in

    def test_upload_route_without_api_key(self):
        response = self.app.post('/upload', data={'file': (b'test.jpg', b'binary_data')})
        self.assertEqual(response.status_code, 401)  # Expecting Unauthorized (401) without API key

    def test_upload_route_with_invalid_api_key(self):
        headers = {'Authorization': 'invalid_api_key'}
        response = self.app.post('/upload', data={'file': (b'test.jpg', b'binary_data')}, headers=headers)
        self.assertEqual(response.status_code, 401)  # Expecting Unauthorized (401) with an invalid API key

    def test_upload_route_with_valid_api_key(self):
        headers = Config.HEADERS  # Use headers from config.py
        response = self.app.post('/upload', data={'file': (b'test.jpg', b'binary_data')}, headers=headers)
        self.assertEqual(response.status_code, 200)  # Expecting success (200) with a valid API key

if __name__ == '__main__':
    unittest.main()
