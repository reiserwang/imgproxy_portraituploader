from flask import Flask, render_template, request, redirect, url_for
from flask_oidc import OpenIDConnect
import os
from werkzeug.utils import secure_filename
from imgproxy import UrlBuilder
import configparser
import cv2
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.config['OIDC_ID_TOKEN_COOKIE_SECURE'] = False
app.config['OIDC_REQUIRE_VERIFIED_EMAIL'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

oidc = OpenIDConnect(app)
config = configparser.ConfigParser()
config.read('imgproxy_config.ini')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_employee_id():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['preferred_username'])
        return user_info.get('preferred_username', 'unknown_employee_id')
    return 'unknown_employee_id'

def is_human_portrait(image_path):
    # Load the image using OpenCV
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use a pre-trained face cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Check if at least one face is detected
    if len(faces) > 0:
        # Get the coordinates of the first detected face
        x, y, w, h = faces[0]

        # Calculate the height of the face
        face_height = h

        # Calculate the height range for the head (60% to 80%)
        min_head_height = 0.6 * face_height
        max_head_height = 0.8 * face_height

        # Check if the head height is within the specified range
        return min_head_height <= h <= max_head_height

    return False

@app.route('/')
def home():
    if oidc.user_loggedin:
        return render_template('home.html')
    else:
        return redirect(url_for('oidc.login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Get employee ID and use it as part of the processed image filename
            employee_id = get_employee_id()
            processed_filename = f"{employee_id}.jpg"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Check if the uploaded photo is a human portrait
            if is_human_portrait(file_path):
                # Process the uploaded photo using imgproxy
                imgproxy_url_builder = UrlBuilder(
                    base_url=config['imgproxy']['base_url'],
                    key=config['imgproxy']['key'],
                    salt=config['imgproxy']['salt']
                )
                processed_url = imgproxy_url_builder.build_url(filename, width=int(config['imgproxy']['width']), height=int(config['imgproxy']['height']))

                return render_template('upload.html', processed_url=processed_url)
            else:
                return render_template('upload.html', error='Uploaded photo is not a valid human portrait.')

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
