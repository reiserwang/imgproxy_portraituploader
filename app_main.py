from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_oidc import OpenIDConnect
import os
from werkzeug.utils import secure_filename
import requests
from config import Config  # Import the Config class from config.py

app = Flask(__name__)
app.config.from_object(Config)  # Use the Config class for configuration
oidc = OpenIDConnect(app)

def get_employee_id():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['preferred_username'])
        return user_info.get('preferred_username', 'unknown_employee_id')
    return 'unknown_employee_id'

def authenticate_request():
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != Config.API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    return None

@app.route('/')
def home():
    if oidc.user_loggedin:
        return render_template('home.html')
    else:
        return redirect(url_for('oidc.login'))

@app.route('/upload', methods=['POST'])
def upload():
    authentication_result = authenticate_request()
    if authentication_result:
        return authentication_result

    if 'file' not in request.files:
        return jsonify({'error': 'File is missing'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'File name is missing'}), 400

    # Get employee ID and use it as part of the processed image filename
    employee_id = get_employee_id()
    processed_filename = f"{employee_id}.jpg"

    file_path = os.path.join('uploads', secure_filename(file.filename))
    file.save(file_path)

    # Redirect to the image processing microservice
    headers = Config.HEADERS
    response = requests.get(f"{Config.IMAGE_PROCESSING_SERVICE_URL}/process_image/{processed_filename}", headers=headers)

    if response.status_code != 200:
        return jsonify({'error': 'Image processing failed'}), 500

    return jsonify({'message': 'Image processing successful', 'processed_url': response.json()['processed_url']})

if __name__ == '__main__':
    app.run(debug=True)
