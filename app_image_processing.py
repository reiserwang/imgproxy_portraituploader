from flask import Flask, jsonify, request
from imgproxy import UrlBuilder
import configparser
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.config['OIDC_ID_TOKEN_COOKIE_SECURE'] = False
app.config['OIDC_REQUIRE_VERIFIED_EMAIL'] = False
app.config['API_KEY'] = 'your_api_key'

config = configparser.ConfigParser()
config.read('imgproxy_config.ini')

def authenticate_request():
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != app.config['API_KEY']:
        return jsonify({'error': 'Unauthorized'}), 401

    return None

@app.route('/process_image/<filename>', methods=['GET'])
def process_image(filename):
    authentication_result = authenticate_request()
    if authentication_result:
        return authentication_result

    # Process the uploaded photo using imgproxy
    imgproxy_url_builder = UrlBuilder(
        base_url=config['imgproxy']['base_url'],
        key=config['imgproxy']['key'],
        salt=config['imgproxy']['salt']
    )

    processed_url = imgproxy_url_builder.build_url(filename, width=int(config['imgproxy']['width']), height=int(config['imgproxy']['height']))

    return jsonify({'processed_url': processed_url})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
