import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect (302) if user is not logged in

    def test_upload_route(self):
        response = self.app.post('/upload', data={'file': (b'test.jpg', b'binary_data')})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect (302) if user is not logged in

if __name__ == '__main__':
    unittest.main()
