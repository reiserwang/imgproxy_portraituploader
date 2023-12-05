import unittest
from flask import Flask, url_for
from app_main import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Expect a redirect when not logged in

    def test_upload_page(self):
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 401)  # Expect unauthorized status when not authenticated

    def test_allowed_file(self):
        self.assertTrue(app.allowed_file('image.jpg'))
        self.assertTrue(app.allowed_file('image.jpeg'))
        self.assertTrue(app.allowed_file('image.png'))
        self.assertTrue(app.allowed_file('image.gif'))
        self.assertFalse(app.allowed_file('text.txt'))
        self.assertFalse(app.allowed_file('document.pdf'))

    def test_get_employee_id(self):
        with app.test_request_context('/'):
            self.assertEqual(app.get_employee_id(), 'unknown_employee_id')

        with app.test_request_context('/?preferred_username=testuser'):
            self.assertEqual(app.get_employee_id(), 'testuser')

    def test_authenticate_request(self):
        with app.test_request_context('/'):
            response = app.authenticate_request()
            self.assertEqual(response.status_code, 401)

    def test_upload_valid_file(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['openid'] = {'preferred_username': 'testuser'}  # Simulate authentication
            with open('test_image.jpg', 'rb') as file:
                response = c.post('/upload', data={'file': (file, 'test_image.jpg')})
                self.assertEqual(response.status_code, 200)

    def test_upload_invalid_file(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['openid'] = {'preferred_username': 'testuser'}  # Simulate authentication
            with open('test_document.pdf', 'rb') as file:
                response = c.post('/upload', data={'file': (file, 'test_document.pdf')})
                self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()