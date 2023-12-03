from flask import Flask, jsonify, request
from imgproxy import UrlBuilder
import configparser
import os
import dlib
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config.from_object('config.Config')

config = configparser.ConfigParser()
config.read('imgproxy.config')

def authenticate_request():
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != app.config['API_KEY']:
        return jsonify({'error': 'Unauthorized'}), 401

    return None

def is_human_head_present(image_path):
    # Load the image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use the dlib face detector
    detector = dlib.get_frontal_face_detector()
    faces = detector(gray)

    # Check if at least one face is detected
    return len(faces) > 0

def head_height_percentage(image_path):
    # Load the image
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    # Use the dlib face detector
    detector = dlib.get_frontal_face_detector()
    faces = detector(img)

    # Calculate the height of the first detected face
    if len(faces) > 0:
        face = faces[0]
        face_height = face.bottom() - face.top()
        return (face_height / height) * 100
    else:
        return 0

def crop_and_resize(image_path, width, height, quality):
    img = Image.open(image_path)

    # Get the coordinates of the detected face
    img_array = np.array(img)
    detector = dlib.get_frontal_face_detector()
    faces = detector(img_array)
    
    if len(faces) > 0:
        face = faces[0]
        left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()

        # Calculate the original aspect ratio
        original_width, original_height = img.size
        original_aspect_ratio = original_width / original_height

        # Calculate the target width or height to maintain the original aspect ratio
        target_width = int(height * original_aspect_ratio)
        target_height = int(width / original_aspect_ratio)

        # Choose the larger dimension to resize
        if target_width <= width:
            target_size = (target_width, height)
        else:
            target_size = (width, target_height)

        # Crop the image to the detected face
        img_cropped = img.crop((left, top, right, bottom))

        # Resize the image to the calculated dimensions
        img_resized = img_cropped.resize(target_size, Image.ANTIALIAS)

        # Save the processed image
        processed_path = os.path.join('uploads', 'processed_' + os.path.basename(image_path))
        img_resized.save(processed_path, format='JPEG', quality=quality)

        return processed_path

    return None

@app.route('/process_image/<filename>', methods=['GET'])
def process_image(filename):
    authentication_result = authenticate_request()
    if authentication_result:
        return authentication_result

    # Check if there's a human head in the portrait photo
    image_path = os.path.join('uploads', filename)
    if not is_human_head_present(image_path):
        return jsonify({'error': 'No human head detected in the photo'}), 400

    # Check if the head occupies more than X% of the photo's height
    min_head_height_percentage = float(config['image_processing']['min_head_height_percentage'])
    actual_head_height_percentage = head_height_percentage(image_path)

    if actual_head_height_percentage < min_head_height_percentage:
        return jsonify({'error': f'Head height is less than {min_head_height_percentage}% of the photo height'}), 400

    # Crop and resize the image
    width = int(config['imgproxy_processing']['width'])
    height = int(config['imgproxy_processing']['height'])
    quality = int(config['imgproxy_processing']['quality'])

    processed_image_path = crop_and_resize(image_path, width, height, quality)

    if processed_image_path:
        return jsonify({'processed_url': processed_image_path})
    else:
        return jsonify({'error': 'Failed to process the image'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
