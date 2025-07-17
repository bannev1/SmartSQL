# <div align="center">SmartSQL</div>

<div align="center"><i>Control your SQL server with natural language</i></div>

***

## Table of Contents

- [SmartSQL](#smartsql)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Functionality](#functionality)
    - [SmartSQL Features](#smartsql-features)
      - [Instantiation](#instantiation)
      - [Querying](#querying)
      - [Backlog](#backlog)
    - [Settings \& Server Descriptions](#settings--server-descriptions)
  - [Contributing](#contributing)

## Introduction

> [!NOTE]
> Note that this is made to work with [Oracle Database](https://en.wikipedia.org/wiki/Oracle_Database). If you are using another flavor of SQL or database provider, please modify the [database.py](Helpers/database.py) file to work with your database.

Control your SQL server with natural language using the OpenAI Azure AI API. Note that this was developed using OpenAI's `o4-mini`.

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

1. Install the requirements in the [requirements.txt](/requirements.txt) file
2. Create an `env_data.env` file (or an environment file and specify its path to the class) with the following structure:

```shell
# OpenAI API
AZURE_OPENAI_API_KEY = "API Key"
AZURE_OPENAI_ENDPOINT = "OpenAI Endpoint"
AZURE_OPENAI_API_VERSION = "API Version"
AZURE_OPENAI_DEPLOYMENT_NAME = "AI Model"
AZURE_AI_KEY = "Azure AI API Key"
AZURE_AI_ENDPOINT = "Azure AI Endpoint"

# Database Connection String - ORACLE
DB_USER = "Username"
DB_PASSWORD = "Password"
DB_DSN = "dbhost.example.com/mydb"

# Database Connection String - POSTGRES
DB_USER = "Username"
DB_PASSWORD = "Password"
DB_NAME = "mydb"
DB_HOST = "dbhost.example.com"
DB_PORT = "0000"
```

*Make sure to replace the information above with your own.*

1. Create a `settings.json` file or a `settings` dictionary. See the [Settings & Server Descriptions](#settings--server-descriptions) section for more information.

2. Use the `query.py` file and the class within it to make your query. A more in-depth explanation is found in the [SmartSQL Features](#smartsql-features) section of this README.

> See [example.py](/example/example.py) for a full example.

## Functionality

### SmartSQL Features

#### Instantiation

To create an instance of the `SmartSQL` class, which will essentially be what you will use to interact with the AI, simply create a `settings` dictionary *(see [Settings & Server Descriptions](#settings--server-descriptions) for an in-depth explanation)* and pass it into the class, like the following:

```python
from query import SmartSQL

settings = ... # See Settings & Server Descriptions for an in-depth explanation 

mySmartSQL = SmartSQL(settings)
```

By default, the SmartSQL class will load the `env_data.env` file to access API keys and connection strings. (See the [usage](#usage) section for a template) If you are using another `.env` file, you can specify it with the `envData` parameter like so:

```python
mySmartSQL = SmartSQL(settings, envData="/path/to/.env")
```

If you do not wish to use a `.env` file, you can alternatively pass each property as an attribute, like so:

```python
mySmartSQL = SmartSQL(settings, 
                    AZURE_OPENAI_API_KEY = "API Key",
                    AZURE_OPENAI_ENDPOINT = "OpenAI Endpoint",
                    AZURE_OPENAI_API_VERSION = "API Version",
                    AZURE_OPENAI_DEPLOYMENT_NAME = "AI Model",
                    AZURE_AI_KEY = "Azure AI API Key",
                    AZURE_AI_ENDPOINT = "Azure AI Endpoint",
                    DB_USER = "Username",
                    DB_PASSWORD = "Password",
                    DB_CONN = "dbhost.example.com/mydb"
                    )
```

Additionally, there exists the parameter `confirmExecute` which is a boolean to check whether you wish for the program to output the generated SQL and prompt if it should execute it, essentially as a security check. For example, if this property were `True`, the following:

Also specify `flavor` which is either `'oracle'` or `'postgres'`

```python
mySmartSQL = SmartSQL(settings, 'oracle', confirmExecute=True)

mySmartSQL.query("Give me a list of all orders made in the past month for this year")
```

Would output something similar to:

```shell
SELECT * FROM OrderTable WHERE Booking_Date >= ADD_MONTHS(TRUNC(SYSDATE,'MM'),-1) AND Booking_Date < TRUNC(SYSDATE,'MM') AND EXTRACT(YEAR FROM Booking_Date)=EXTRACT(YEAR FROM SYSDATE)

Execute? [Y/N] 
```

If `y` is inputted, it will then execute the SQL on the database. Otherwise the command is stored for future use. 

Note this feature can be overridden by the `.query()` method's `confirmExecute` parameter.

#### Querying

To make a query, use the `.query()` method and specify the query you wish to make. Assuming `confirmExecute` is false, it will generate an SQL command and execute it directly to the database. It will then return a `list` containing any potential results.

For example, the following:

```python
mySmartSQL.query("Give me a list of all orders made in the past month for this year")
```

Would generate SQL code similar to:

```shell
SELECT * FROM OrderTable WHERE Booking_Date >= ADD_MONTHS(TRUNC(SYSDATE,'MM'),-1) AND Booking_Date < TRUNC(SYSDATE,'MM') AND EXTRACT(YEAR FROM Booking_Date)=EXTRACT(YEAR FROM SYSDATE)
```

Additionally, there exists the parameter `confirmExecute` which is a boolean to check whether you wish for the program to output the generated SQL and prompt if it should execute it, essentially as a security check. For example, if this property were `True`, the following:

```python
mySmartSQL = SmartSQL(settings, confirmExecute=True)

mySmartSQL.query("Give me a list of all orders made in the past month for this year")
```

Would output something similar to:

```shell
SELECT * FROM OrderTable WHERE Booking_Date >= ADD_MONTHS(TRUNC(SYSDATE,'MM'),-1) AND Booking_Date < TRUNC(SYSDATE,'MM') AND EXTRACT(YEAR FROM Booking_Date)=EXTRACT(YEAR FROM SYSDATE)

Execute? [Y/N] 
```

If `y` is inputted, it will then execute the SQL on the database. Otherwise the command is stored for future use.

#### Backlog

Assuming the commands ran through the AI modify the database directly, a backlog is kept (stored in `SmartSQL().ai.backlog`) of all commands run, assuming `withBacklog` is true, which is then passed to the AI model so it understands what has been changed. For example the following

```python
mySmartSQL.query("Delete the table Orders")
```

would delete a table, a change permanently modifying the database and meaning the `settings` dictionary no longer accurately represents the database. Therefore the backlog will store all these queries and changes for the AI to understand the current and most accurate state of the database.

If a new `settings` dictionary is generated, you can use the `.updateSettings()` method to clear the backlog and update `settings` with a new `settings` dictionary. For example:

```python
mySmartSQL.query("Delete the table Orders") # Permanent change

newSettings = ... # Generate new settings

mySmartSQL.updateSettings(newSettings) # Clear backlog and use newSettings as the new settings
```

### Settings & Server Descriptions

To allow the AI to understand the structure of the server, and to avoid repeat explanations, this project uses a custom layout known as `settings`. It is saved as a `.json` and is processed as a dictionary. To see an example of this layout, view the [settings.json](/example/settings.json) template.

These can be easily generated through 2 main methods:
- With AI and natural language
- Connecting directly to the database and manually inputting relevant descriptions

Both these methods exist in the [settingsManager.py](/settingsManager.py) module.

If you wish to use AI and natural language to generate this `.json`/dictionary, meaning you describe the structure of the database, you can use the following:

> Note that it is recommended to pass in the `CREATE TABLE` SQL queries as a string in the description as well to better explain the structure, however this is optional.

```python
import settingsManager

ENV_PATH = "env_data.env" # Path to environment variables [IF USING]

serverDescription = "My server has 2 tables, Orders and People, where each person has an order and each order has a person, and each order contains a name, timestamp, and ...."

# If using environment variables
settings: dict = settingsManager.settingsWithAIPath(serverDescription, ENV_PATH)

# Otherwise specify manually with dictionary
settings: dict = settingsManager.settingsWithAI(serverDescription, {
    "API_KEY": ...,
})
```

To connect it to the database and use that to auto-generate,

> [!NOTE]
> If not using Oracle Database, you might have to modify the SQL queries in [settingsManager.py](/settingsManager.py)

```python
import settingsManager

ENV_PATH = "env_data.env" # Path to environment variables [IF USING]

# If using environment variables
settings: dict = settingsManager.settingsFromDBPath(ENV_PATH)

# Otherwise specify manually with dictionary
settings: dict = settingsManager.settingsFromDB({
    "DB_USER": ...,
})
```

If you wish to export/save settings to a JSON,

```python
settingsManager.exportSettings(settings, "/path/to/settings.json") # Export settings
```

If you want to load a `settings.json`,

```python
settingsManager.parseSettings("/path/to/settings.json")
```

## Contributing

If you want to contribute to this project, please follow the guidelines below:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes and commit them
4. Push the new branch to your fork
5. Submit a pull request

We are grateful for the support of our community and for the contributions of everyone who has helped make this project what it is.
