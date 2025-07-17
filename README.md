# <div align="center">SmartSQL</div>

<div align="center"><i>Control your SQL server with natural language</i></div>

***

## Table of Contents

- [SmartSQL](#smartsql)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)

## Introduction

> [!NOTE]
> Note that this is made to work with [Oracle Database](https://en.wikipedia.org/wiki/Oracle_Database). If you are using another flavor of SQL or database provider, please modify the [database.py](Helpers/database.py) file to work with your database.

Control your SQL server with natural language using the OpenAI Azure AI API.

## Installation

To install the required packages, run the following command:

```shell
pip install -r requirements.txt
```

Or, depending on your installation:

```shell
pip3 install -r requirements.txt
```

## Usage

To use the project, you can:

1. Install the requirements in the `requirements.txt` file
2. Create an `env_data.env` file (or an environment file and specify its path to the class) with the following structure:

```shell
# OpenAI API
AZURE_OPENAI_API_KEY = "API Key"
AZURE_OPENAI_ENDPOINT = "OpenAI Endpoint"
AZURE_OPENAI_API_VERSION = "API Version"
AZURE_OPENAI_DEPLOYMENT_NAME = "AI Model"
AZURE_AI_KEY = "Azure AI API Key"
AZURE_AI_ENDPOINT = "Azure AI Endpoint"

# Database Connection String
DB_USER = "Username"
DB_PASSWORD = "Password"
DB_DSN = "dbhost.example.com/mydb"
```

*Make sure to replace the information above with your own.*

3. Use the `query.py` file and the class within it to make your query 

Example usage:

> See [example.py](example.py) for a full example.

```python
# Import the class
from query import SmartSQL

# Define properties
TABLELAYOUT = {
    "My table"
}

# Create instance to connect to database
processor = SmartSQL()
```

If you don't want to create a `.env` file, you can also directly pass in the data like the following:

```python


```

For full functionality, you can also create a `.json` file (see )


## Contributing

If you want to contribute to this project, please follow the guidelines below:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes and commit them
4. Push the new branch to your fork
5. Submit a pull request

We are grateful for the support of our community and for the contributions of everyone who has helped make this project what it is.
