# Imgproxy Portrait Uploader

A Python Flask sample code using AAD for authentication, allowing employee to upload to upload their portrait photo, making some simple checks e.g. headarea ratio using OpenCV, and transforming the format and dimension using imgproxy in micro service architecture with cintainer as an option.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
  - [Azure AD Configuration](#azure-ad-configuration)
  - [Microservice Configuration](#microservice-configuration)
  - [imgproxy Configuration](#imgproxy-configuration)
  - [Docker](#docker)
- [Test](#test)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

Make sure you have the following installed:

- [Python](https://www.python.org/) (version x.x.x)
- [pip](https://pypi.org/project/pip/) (version x.x.x)

### Installation

1. Clone the repository:

    ```bash
   git clone https://github.com/your-username/your-project.git
    ```
2. Navigate to the project directory:
    ```bash
   cd your-project
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
1. Start the main Flask application:
    ```bash
    python app_main.py
    ```

2. Start the image processing microservice in a separate terminal:
     ```bash
    python app_image_processing.py
    ```
3. Visit http://localhost:5000 in your web browser.

### Configuration

#### Azure AD Configuration
Create an Azure AD application and obtain the client ID and client secret.
Update the client_secrets.json file with your Azure AD credentials.

#### Microservice Configuration
Make sure to replace 'your_secret_key' and 'your_api_key' in config.py with your actual secret and API key values. Additionally, ensure that the configuration values match your actual setup, including the URL for the image processing microservice.

#### imgproxy Configuration
Configure imgproxy by updating the imgproxy.config file with your settings.

#### Docker
1. For the main Flask application:

    ```bash
    docker build -t your_main_app_image -f Dockerfile_main .
    ```

2. For the image processing microservice:

    ```bash
    docker build -t your_image_processing_image -f Dockerfile_image_processing .

    ```
3. Replace your_main_app_image and your_image_processing_image with the desired names for your Docker images.

4. Run the Docker containers:
    - For the main Flask application:

    ```bash
    docker run -p 5000:5000 your_main_app_image
    ```

    - For the image processing microservice:

    ```bash
    docker run -p 5001:5001 your_image_processing_image
    ```

### Test
To run unit tests, use the following command:

    ``bash
    python -m unittest test_app.py
    ```

