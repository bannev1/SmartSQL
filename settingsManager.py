import json
import os
from dotenv import load_dotenv

from Helpers import Database, Prompter


# Export
def exportSettings(settings: dict, exportPath: str = "./settings.json") -> None:
    """
    Export settings to JSON file as a dictionary

    Args:
        exportPath (str): Path to export JSON file to
    """

    # Open and export
    with open(exportPath, 'r+') as file:
        json.dump(settings, file)


# Get settings from database directly (without descriptions)
def settingsFromDB(envPath: str = 'env_data.env') -> dict:
    """
    Generate settings from database directly with AI
    
    Note descriptions will be set as an empty string, and will have to be manually explained.

    Args:
        envPath (str): Environment variables .env file path to process connection string
    """

    # Load environment variables
    load_dotenv(envPath)

    # Process
    return settingsFromDB(
        {
            "DB_USER": os.getenv('DB_USER'),
            "DB_PASSWORD": os.getenv('DB_PASSWORD'),
            "DB_DSN": os.getenv('DB_DSN')
        }
    )

def settingsFromDB(connection: dict[str]) -> dict:
    """
    Generate settings from database directly with AI. 
    
    Note descriptions will be set as an empty string, and will have to be manually explained.

    Args:
        connection (dict[str]): Connection properties. See README for exact structure
    """

    # Connect DB
    db = Database(connection)

    # Get all tables
    tableNames = db.execute("SELECT table_name FROM dba_tables;")

    tables = []

    # Get all fields
    for tableName in tableNames:
        table = {
            'Name': tableName,
            'Description': ''
        }

        layout = []

        fields = db.execute(f"SELECT column_name, data_type FROM all_tab_cols WHERE table_name = '{tableName}';")[0]

        for field in fields:
            struct = {
                'Name': field['column_name'],
                'Type': field['data_type'],
                'Description': ''
            }


        tables.append(table)


# AI Settings
def settingsWithAI(details: str, envPath: str) -> dict:
    """
    Use AI to generate the settings dictionary, given details about database

    Args:
        details (str): String explaining database layout
    """

    # Load environment variables
    load_dotenv(envPath)

    # Process
    return settingsWithAI(
        details,
        {
            "AZURE_OPENAI_API_KEY": os.getenv('AZURE_OPENAI_API_KEY'),
            "AZURE_OPENAI_ENDPOINT": os.getenv('AZURE_OPENAI_ENDPOINT'),
            "AZURE_OPENAI_API_VERSION": os.getenv('AZURE_OPENAI_API_VERSION'),
            "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            "AZURE_AI_KEY": os.getenv('AZURE_AI_KEY'),
            "AZURE_AI_ENDPOINT": os.getenv('AZURE_AI_ENDPOINT')
        }
    )

def settingsWithAI(details: str, apiKeys: dict) -> dict:
    """
    Use AI to generate the settings dictionary, given details about database

    Args:
        details (str): String explaining database layout
    """

    settingsTemplate = json.dumps(EXAMPLE_SETTINGS, indent='\t') # Get settings layout for AI

    ai = Prompter(apiKeys)

    basePrompt = f"Given a description of the database, you should output a JSON file (make sure to not output anything else) similar to the following template for their database.\n\nTemplate: \n{settingsTemplate}"

    result = json.loads(ai.prompt(basePrompt, details))

    return result


# Parse JSON
def parseSettings(settingsPath: str) -> dict:
    """
    Parse JSON path to get settings

    Args:
        settingsPath (str): Path of settings/JSON file
    """

    return json.loads(settingsPath)




# EXAMPLE SETTINGS/TEMPLATE
EXAMPLE_SETTINGS = {
    "Server_Name": "My Server",
    "Server_Description": "Brief Server Description",
    "SQL_Flavor": "Oracle Database",
    "Tables": [
        {
            "Name": "Table 1 Name",
            "Description": "Table 1 Description",
            "Layout": [
                {
                    "Name": "Field 1 Name",
                    "Type": "String",
                    "Description": "Explanation of what field 1 is for/contains",
                    "Properties": {
                        "isPrimaryKey": True,
                        "Foreign_Reference": "",
                        "Constraints": "NOT NULL"
                    }
                },

                {
                    "Name": "Field 2 Name",
                    "Type": "Boolean",
                    "Description": "Explanation of what field 2 is for/contains",
                    "Properties": {
                        "isPrimaryKey": False,
                        "Foreign_Reference": "Table 2 Name",
                        "Constraints": ""
                    }
                }
            ]
        },

        {
            "Name": "Table 2 Name",
            "Description": "Table 2 Description",
            "Layout": [
                {
                    "Name": "Field 1 Name",
                    "Type": "Integer",
                    "Description": "Explanation of what field 1 is for/contains",
                    "Properties": {
                        "isPrimaryKey": True,
                        "Foreign_Reference": "",
                        "Constraints": "NOT NULL"
                    }
                },

                {
                    "Name": "Field 2 Name",
                    "Type": "VARCHAR2(50)",
                    "Description": "Explanation of what field 2 is for/contains",
                    "Properties": {
                        "isPrimaryKey": False,
                        "Foreign_Reference": "",
                        "Constraints": ""
                    }
                }
            ]
        }
    ]
}