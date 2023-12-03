# config.py
'''
Remember to keep the config.py file secure, especially if it contains sensitive information like API keys. 
Additionally, it's recommended not to include sensitive information in version control systems. 
You might want to use environment variables or a configuration management tool to handle sensitive information in production environments.
'''

class Config:
    SECRET_KEY = 'your_secret_key'
    OIDC_CLIENT_SECRETS = 'client_secrets.json'
    OIDC_ID_TOKEN_COOKIE_SECURE = False
    OIDC_REQUIRE_VERIFIED_EMAIL = False

    IMAGE_PROCESSING_SERVICE_URL = 'http://image-processing-service:5001'
    API_KEY = 'your_api_key'
    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'User-Agent': 'YourApp/1.0',
        # Add any other headers as needed for your specific API request
    }
