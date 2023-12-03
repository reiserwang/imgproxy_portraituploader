# Your Project Name

Brief description or introduction to your project.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
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
    ```bash
    pip install -r requirements.txt
    ```
    Visit http://localhost:5000 in your web browser.

### Configuration

#### Azure AD Configuration
Create an Azure AD application and obtain the client ID and client secret.
Update the client_secrets.json file with your Azure AD credentials.

#### imgproxy Configuration
Configure imgproxy by updating the imgproxy_config.ini file with your settings.

### Test
To run unit tests, use the following command:
    ``bash
    python -m unittest test_app.py
    ```

