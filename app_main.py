from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_oidc import OpenIDConnect
import os
from werkzeug.utils import secure_filename
import aiohttp
import asyncio
from config import Config  # Import the Config class from config.py

app = Flask(__name__)
app.config.from_object(Config)  # Use the Config class for configuration
oidc = OpenIDConnect(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_employee_id():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['preferred_username'])
        return user_info.get('preferred_username', 'unknown_employee_id')
    return 'unknown_employee_id'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def authenticate_request():
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != Config.API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    return None

async def upload_file(file, employee_id):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)
    return file_path

async def process_image(file_path, employee_id, session):
    # You can use aiohttp to make asynchronous requests to the image processing service
    # For demonstration purposes, let's assume the image processing service is running locally on port 5001
    image_processing_url = f'http://localhost:5001/process_image'
    data = {'image_paths': [file_path]}
    
    async with session.post(image_processing_url, json=data) as response:
        result = await response.json()

    return result.get(file_path, {})

async def handle_uploaded_file(file, employee_id, session):
    file_path = await upload_file(file, employee_id)
    result = await process_image(file_path, employee_id, session)
    return result

async def process_files(files, employee_id):
    async with aiohttp.ClientSession() as session:
        tasks = [handle_uploaded_file(file, employee_id, session) for file in files]
        return await asyncio.gather(*tasks)

@app.route('/', methods=['GET', 'POST'])
async def home():
    if not oidc.user_loggedin:
        return redirect(url_for('oidc.login'))

    if request.method == 'POST':
        authentication_result = await authenticate_request()
        if authentication_result:
            return authentication_result

        files = request.files.getlist('file')

        if not files:
            return jsonify({'error': 'No files provided'}), 400

        employee_id = get_employee_id()
        results = await process_files(files, employee_id)

        return render_template('result_async.html', results=results)

    return render_template('home_async.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
