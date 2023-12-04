import unittest
from unittest.mock import patch, MagicMock
from app_image_processing import app, is_human_head_present, head_height_percentage, crop_and_resize
from PIL import Image

class TestAppImageProcessing(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('app_image_processing.cv2')
    def test_is_human_head_present_with_face(self, mock_cv2):
        mock_cv2.imread.return_value = None
        mock_cv2.cvtColor.return_value = None
        mock_cv2.get_frontal_face_detector.return_value = MagicMock(return_value=[MagicMock()])
        result = is_human_head_present('test_image.jpg')
        self.assertTrue(result)

    @patch('app_image_processing.cv2')
    def test_is_human_head_present_without_face(self, mock_cv2):
        mock_cv2.imread.return_value = None
        mock_cv2.cvtColor.return_value = None
        mock_cv2.get_frontal_face_detector.return_value = MagicMock(return_value=[])
        result = is_human_head_present('test_image.jpg')
        self.assertFalse(result)

    @patch('app_image_processing.cv2')
    def test_head_height_percentage_with_face(self, mock_cv2):
        mock_cv2.imread.return_value = None
        mock_cv2.shape.return_value = (100, 200, 3)
        mock_cv2.get_frontal_face_detector.return_value = MagicMock(return_value=[MagicMock(top=10, bottom=80)])
        result = head_height_percentage('test_image.jpg')
        self.assertEqual(result, 70.0)

    @patch('app_image_processing.cv2')
    def test_head_height_percentage_without_face(self, mock_cv2):
        mock_cv2.imread.return_value = None
        mock_cv2.shape.return_value = (100, 200, 3)
        mock_cv2.get_frontal_face_detector.return_value = MagicMock(return_value=[])
        result = head_height_percentage('test_image.jpg')
        self.assertEqual(result, 0)

    @patch('app_image_processing.Image')
    @patch('app_image_processing.dlib')
    def test_crop_and_resize_with_face(self, mock_dlib, mock_image):
        mock_dlib.get_frontal_face_detector.return_value = MagicMock(return_value=[MagicMock(left=10, top=20, right=60, bottom=80)])
        mock_image.open.return_value.size = (200, 100)
        mock_image.ANTIALIAS = 'ANTIALIAS'
        mock_cropped = MagicMock()
        mock_resized = MagicMock()
        mock_image.open.return_value.crop.return_value = mock_cropped
        mock_cropped.resize.return_value = mock_resized
        mock_resized.save.return_value = None

        result = crop_and_resize('test_image.jpg', 120, 160, 90)

        self.assertIsNotNone(result)
        mock_image.open.assert_called_with('test_image.jpg')
        mock_image.open.return_value.crop.assert_called_with((10, 20, 60, 80))
        mock_cropped.resize.assert_called_with((120, 160), 'ANTIALIAS')
        mock_resized.save.assert_called_with('uploads/processed_test_image.jpg', format='JPEG', quality=90)

    @patch('app_image_processing.Image')
    @patch('app_image_processing.dlib')
    def test_crop_and_resize_without_face(self, mock_dlib, mock_image):
        mock_dlib.get_frontal_face_detector.return_value = MagicMock(return_value=[])
        mock_image.open.return_value.size = (200, 100)

        result = crop_and_resize('test_image.jpg', 120, 160, 90)

        self.assertIsNone(result)
        mock_image.open.assert_called_with('test_image.jpg')
        mock_dlib.get_frontal_face_detector.assert_called_with(mock_image.open.return_value)

if __name__ == '__main__':
    unittest.main()
