from flask import Flask, jsonify, request
from imgproxy import UrlBuilder
import configparser
import os
import dlib
import cv2
import numpy as np
from PIL import Image
import asyncio

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
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    faces = detector(gray)
    return len(faces) > 0

def head_height_percentage(image_path):
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    detector = dlib.get_frontal_face_detector()
    faces = detector(img)
    if len(faces) > 0:
        face = faces[0]
        face_height = face.bottom() - face.top()
        return (face_height / height) * 100
    else:
        return 0

async def crop_and_resize(image_path, width, height, quality, result_dict):
    img = Image.open(image_path)
    img_array = np.array(img)
    detector = dlib.get_frontal_face_detector()
    faces = detector(img_array)
    
    if len(faces) > 0:
        face = faces[0]
        left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()

        original_width, original_height = img.size
        original_aspect_ratio = original_width / original_height

        target_width = int(height * original_aspect_ratio)
        target_height = int(width / original_aspect_ratio)

        if target_width <= width:
            target_size = (target_width, height)
        else:
            target_size = (width, target_height)

        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize(target_size, Image.ANTIALIAS)

        processed_path = os.path.join('uploads', 'processed_' + os.path.basename(image_path))
        img_resized.save(processed_path, format='JPEG', quality=quality)

        result_dict[image_path] = processed_path

async def process_image(image_path, width, height, quality, result_dict):
    authentication_result = authenticate_request()
    if authentication_result:
        result_dict[image_path] = {'error': 'Unauthorized'}
        return

    if not is_human_head_present(image_path):
        result_dict[image_path] = {'error': 'No human head detected in the photo'}
        return

    min_head_height_percentage = float(config['image_processing']['min_head_height_percentage'])
    actual_head_height_percentage = head_height_percentage(image_path)

    if actual_head_height_percentage < min_head_height_percentage:
        result_dict[image_path] = {'error': f'Head height is less than {min_head_height_percentage}% of the photo height'}
        return

    await crop_and_resize(image_path, width, height, quality, result_dict)

@app.route('/process_image/<filename>', methods=['GET'])
async def process_image_route(filename):
    width = int(config['imgproxy_processing']['width'])
    height = int(config['imgproxy_processing']['height'])
    quality = int(config['imgproxy_processing']['quality'])

    result_dict = {}
    await process_image(filename, width, height, quality, result_dict)

    result = result_dict.get(filename, {})

    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    elif result:
        return jsonify({'processed_url': result})
    else:
        return jsonify({'error': 'Failed to process the image'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
