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
    with open(exportPath, 'w+') as file:
        json.dump(settings, file, indent='\t')


# Get settings from database directly (without descriptions)
def settingsFromDBPath(envPath: str = 'env_data.env') -> dict:
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

# NOTE: Might have to modify this if using other database provider (not Oracle Database)
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

        # Get fields
        fields = db.execute(f"SELECT column_name, data_type FROM all_tab_cols WHERE table_name = '{tableName}';")[0]

        # Get primary key - From https://stackoverflow.com/questions/9016578/how-to-get-primary-key-column-in-oracle
        primaryKey = db.execute(f"""SELECT column_name FROM all_cons_columns WHERE constraint_name = (
                                    SELECT constraint_name FROM all_constraints 
                                    WHERE UPPER(table_name) = UPPER('{tableName}') AND CONSTRAINT_TYPE = 'P'
                                );""")[0]['column_name']

        # Look through fields/columns within table
        for field in fields:
            struct = {
                'Name': field['column_name'],
                'Type': field['data_type'],
                'Description': '',
            }

            constraints = db.execute(f"SELECT constraint_type FROM all_constraints WHERE table_name = '{tableName}';")

            properties = {
                'isPrimaryKey': struct['Name'].strip() == primaryKey.strip(),
                'Foreign_Reference': '',
                'Constraints': []
            }

            # Get constraints
            for constraint in constraints:
                constraintType = constraint['constraint_type']

                # Skip if defining primary key
                if constraintType == 'P':
                    continue

                properties["Constraints"].append(constraintType)
            
            struct['Properties'] = properties
            layout.append(struct)
        
        # Add
        table['Layout'] = layout

        tables.append(table)
    
    # Set structure
    settings = {
        'Server_Name': '',
        'Server_Description': '',
        'SQL_Flavor': 'Oracle Database',
        'Tables': tables
    }

    return settings


# AI Settings
def settingsWithAIPath(details: str, envPath: str) -> dict:
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

    basePrompt = f"Given a description of the database, you should output a JSON file (make sure to not output anything else, and do NOT put it in a code block and do NOT add comments. Just raw text) similar to the following template for their database.\n\nTemplate: \n{settingsTemplate}"

    result = json.loads(ai.prompt(basePrompt, details).strip())

    return result


# Parse JSON
def parseSettings(settingsPath: str) -> dict:
    """
    Parse JSON path to get settings

    Args:
        settingsPath (str): Path of settings/JSON file
    """

    with open(settingsPath, 'r+') as file:
        return json.loads('\n'.join(file.readlines()))


# Find table from name
def findTable(settings: dict, tableName: str) -> dict:
    """
    Find table in settings given tableName, returning table dictionary

    Args:
        settings (dict): Settings dictionary
        tableName (str): Name of table
    """

    table = [i for i in settings['Tables'] if i['Name'] == tableName][0]

    return table


# Get all tables
def getAllTables(settings: dict) -> list[str]:
    """
    Get a list of all tables available

    Args:
        settings (dict): Settings dictionary
    """

    return [i['Name'] for i in settings['Tables']]


# EXAMPLE SETTINGS/TEMPLATE
EXAMPLE_SETTINGS = {
	"Server_Name": "My_Server",
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
						"Constraints": [
							"NOT NULL"
						]
					}
				},

				{
					"Name": "Field 2 Name",
					"Type": "Boolean",
					"Description": "Explanation of what field 2 is for/contains",
					"Properties": {
						"isPrimaryKey": False,
						"Constraints": []
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
						"Constraints": [
							"NOT NULL"
						]
					}
				},

				{
					"Name": "Field 2 Name",
					"Type": "VARCHAR2(50)",
					"Description": "Explanation of what field 2 is for/contains",
					"Properties": {
						"isPrimaryKey": False,
						"Constraints": [
							"NOT NULL",
							"IN 'String 1', 'String 2'"
						]
					}
				},

				{
					"Name": "Field 3 Name",
					"Type": "VARCHAR2(50)",
					"Description": "Explanation of what field 3 is for/contains",
					"Properties": {
						"isPrimaryKey": False,
						"Constraints": [
							"UNIQUE"
						]
					}
				}
			]
		}
	]
}
