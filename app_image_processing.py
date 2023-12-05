from flask import Flask, jsonify, request
from imgproxy import UrlBuilder
import configparser
import os
import multiprocessing as mp
import cv2
import numpy as np
from PIL import Image
from mmap import mmap

# Shared memory for communication between main and worker processes
shared_memory = mmap(-1, 1024)

app = Flask(__name__)
app.config.from_object('config.Config')

config = configparser.ConfigParser()
config.read('imgproxy.config')

# Define worker processes
worker_processes = []
for _ in range(int(config['server']['worker_processes'])):
    process = mp.Process(target=process_image, args=())
    process.daemon = True
    process.start()
    worker_processes.append(process)

def authenticate_request(headers):
    api_key = headers.get('Authorization')
    if not api_key or api_key != app.config['API_KEY']:
        return jsonify({'error': 'Unauthorized'}), 401

    return None

def process_image():
    while True:
        # Get filename from shared memory
        filename = shared_memory.readline().decode('utf-8').rstrip('\n')

        if filename == '':
            break

        image_path = os.path.join('uploads', filename)

        # Optimize image processing
        # Use OpenCV's Haar cascades for faster face detection
        face_cascade = cv2.CascadeClassifier(config['haar_cascade_path'])

        # Load and pre-scale image for faster processing
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_resized = cv2.resize(img, (400, 300))

        # Detect faces in the resized image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            # Cache frequently accessed data
            min_head_height_percentage = float(config['image_processing']['min_head_height_percentage'])

            # Calculate head height percentage
            face = faces[0]
            face_height = face[3]
            actual_head_height_percentage = (face_height / img_resized.shape[0]) * 100

            # Check if head height meets minimum requirements
            if actual_head_height_percentage < min_head_height_percentage:
                error_message = f'Head height is less than {min_head_height_percentage}% of the photo height'
                shared_memory.write(jsonify({'error': error_message}).dumps().encode())
                continue

            # Crop and resize the detected face
            left, top, width, height = face
            img_cropped = img_resized[top:top + height, left:left + width]
            target_width = int(config['imgproxy_processing']['width'])
            target_height = int(config['imgproxy_processing']['height'])
            img_resized = cv2.resize(img_cropped, (target_width, target_height))

            # Save the processed image
            processed_path = os.path.join('uploads', 'processed_' + os.path.basename(image_path))
            cv2.imwrite(processed_path, img_resized)

            # Write processed image URL to shared memory
            shared_memory.write(jsonify({'processed_url': processed_path}).dumps().encode())
        else:
            shared_memory.write(jsonify({'error': 'No human head detected in the photo'}).dumps().encode())

@app.route('/process_image/<filename>', methods=['GET'])
def process_image_handler(filename):
    # Signal worker process to start processing the image
    shared_memory.write(filename.encode())
    # Wait for the result from shared memory
    result = shared_memory.readline().decode('utf-8').rstrip('\n')

    # Respond to client
    response = jsonify(eval(result))
    status_code = 400 if 'error' in result else 200
    return response, status_code

if __name__ == '__main__':
    app.run(port=5001, debug=True)
