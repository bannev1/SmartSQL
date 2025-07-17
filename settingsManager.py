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
def settingsFromDBPath(flavor: str, envPath: str = 'env_data.env') -> dict:
    """
    Generate settings from database directly with AI
    
    Note descriptions will be set as an empty string, and will have to be manually explained.

    Args:
        flavor (str): SQL flavor. Currently only 'oracle' or 'postgres' available
        envPath (str): Environment variables .env file path to process connection string
    """

    # Load environment variables
    load_dotenv(envPath)

    # Process
    return settingsFromDB(
        flavor,
        {
            "DB_USER": os.getenv('DB_USER'),
            "DB_PASSWORD": os.getenv('DB_PASSWORD'),
            "DB_NAME": os.getenv('DB_NAME'),
            "DB_HOST": os.getenv('DB_HOST'),
            "DB_PORT": os.getenv('DB_PORT'),
        } if flavor == 'postgres' else {
            "DB_USER": os.getenv('DB_USER'),
            "DB_PASSWORD": os.getenv('DB_PASSWORD'),
            "DB_DSN": os.getenv('DB_DSN'),
        }
    )

# NOTE: Might have to modify this if using other database provider
def settingsFromDB(flavor: str, connection: dict[str]) -> dict:
    """
    Generate database schema with detailed constraint information including CHECK conditions.
    
    Args:
        flavor (str): Database flavor - 'oracle' or 'postgres'
        connection (dict): Connection parameters
        
    Returns:
        dict: Schema structure with tables, columns, and constraints
        
    Example Output:
        {
            "Server_Name": "",
            "Server_Description": "",
            "SQL_Flavor": "PostgreSQL",
            "Tables": [
                {
                    "Name": "employees",
                    "Description": "",
                    "Layout": [
                        {
                            "Name": "id",
                            "Type": "integer",
                            "Description": "",
                            "Properties": {
                                "isPrimaryKey": true,
                                "Foreign_Reference": "",
                                "Constraints": ["PRIMARY KEY"]
                            }
                        },
                        {
                            "Name": "age",
                            "Type": "integer",
                            "Description": "",
                            "Properties": {
                                "isPrimaryKey": false,
                                "Foreign_Reference": "",
                                "Constraints": [
                                    "CHECK (age > 18)",
                                    "NOT NULL"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    """
    db = Database(connection, flavor)
    tables = []

    try:
        if flavor.lower() == 'oracle':
            # Get all user tables
            tableNames = [row[0] for row in db.execute("SELECT table_name FROM user_tables;")]
            
            for tableName in tableNames:
                table = {'Name': tableName, 'Description': ''}
                layout = []
                
                # Get all columns
                columns = db.execute(f"""
                    SELECT column_name, data_type, nullable 
                    FROM user_tab_columns 
                    WHERE table_name = '{tableName}'
                    ORDER BY column_id;
                """)
                
                # Get primary key
                pk_result = db.execute(f"""
                    SELECT cols.column_name 
                    FROM user_constraints cons
                    JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name
                    WHERE cons.table_name = '{tableName}'
                    AND cons.constraint_type = 'P';
                """)
                pk_columns = [row[0] for row in pk_result]
                
                # Get all constraints for the table
                constraints = db.execute(f"""
                    SELECT c.constraint_name, c.constraint_type, c.search_condition, 
                           cols.column_name, c.r_constraint_name
                    FROM user_constraints c
                    LEFT JOIN user_cons_columns cols ON c.constraint_name = cols.constraint_name
                    WHERE c.table_name = '{tableName}'
                    ORDER BY c.constraint_name;
                """)
                
                # Organize constraints by column
                constraint_map = {col[0]: [] for col in columns}
                for const in constraints:
                    const_name, const_type, condition, col_name, r_constraint = const
                    
                    if const_type == 'P':
                        continue  # Already handled with pk_columns
                    elif const_type == 'R':  # Foreign key
                        ref_table_result = db.execute(f"""
                            SELECT table_name 
                            FROM user_constraints 
                            WHERE constraint_name = '{r_constraint}';
                        """)
                        if ref_table_result:
                            ref_table = ref_table_result[0][0]
                            constraint_map[col_name].append(
                                f"FOREIGN KEY REFERENCES {ref_table}({col_name})"
                            )
                    elif const_type == 'U':  # Unique
                        constraint_map[col_name].append("UNIQUE")
                    elif const_type == 'C':  # Check
                        if condition:
                            constraint_map[col_name].append(f"CHECK ({condition})")
                    elif const_type == 'O':  # Read only
                        constraint_map[col_name].append("READ ONLY")
                
                # Build column structures
                for col_name, data_type, nullable in columns:
                    struct = {
                        'Name': col_name,
                        'Type': data_type,
                        'Description': '',
                        'Properties': {
                            'isPrimaryKey': col_name in pk_columns,
                            'Foreign_Reference': '',
                            'Constraints': constraint_map.get(col_name, [])
                        }
                    }
                    
                    # Add NOT NULL if applicable
                    if nullable == 'N':
                        struct['Properties']['Constraints'].append("NOT NULL")
                    
                    layout.append(struct)
                
                table['Layout'] = layout
                tables.append(table)

        elif flavor.lower() == 'postgres':
            # Get all user tables
            tableNames = [row[0] for row in db.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_type = 'BASE TABLE';
            """)]
            
            for tableName in tableNames:
                table = {'Name': tableName, 'Description': ''}
                layout = []
                
                # Get all columns with nullability
                columns = db.execute(f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = '{tableName}'
                    ORDER BY ordinal_position;
                """)
                
                # Get primary key
                pk_result = db.execute(f"""
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = '{tableName}'::regclass
                    AND i.indisprimary;
                """)
                pk_columns = [row[0] for row in pk_result]
                
                # Get all constraints for the table
                constraints = db.execute(f"""
                    SELECT con.conname, con.contype, pg_get_constraintdef(con.oid),
                           a.attname, confrelid::regclass
                    FROM pg_constraint con
                    JOIN pg_class cl ON cl.oid = con.conrelid
                    LEFT JOIN pg_attribute a ON a.attnum = ANY(con.conkey) AND a.attrelid = con.conrelid
                    WHERE cl.relname = '{tableName}'
                    ORDER BY con.conname;
                """)
                
                # Organize constraints by column
                constraint_map = {col[0]: [] for col in columns}
                for const in constraints:
                    const_name, const_type, const_def, col_name, ref_table = const
                    
                    if const_type == 'p':
                        continue  # Primary key already handled
                    elif const_type == 'f':  # Foreign key
                        if col_name:
                            constraint_map[col_name].append(
                                f"FOREIGN KEY {const_def.split('FOREIGN KEY')[1]}"
                            )
                    elif const_type == 'u':  # Unique
                        if col_name:
                            constraint_map[col_name].append("UNIQUE")
                    elif const_type == 'c':  # Check
                        if col_name:
                            constraint_map[col_name].append(const_def)
                
                # Build column structures
                for col_name, data_type, is_nullable in columns:
                    struct = {
                        'Name': col_name,
                        'Type': data_type,
                        'Description': '',
                        'Properties': {
                            'isPrimaryKey': col_name in pk_columns,
                            'Foreign_Reference': '',
                            'Constraints': constraint_map.get(col_name, [])
                        }
                    }
                    
                    # Add NOT NULL if applicable
                    if is_nullable == 'NO':
                        struct['Properties']['Constraints'].append("NOT NULL")
                    
                    layout.append(struct)
                
                table['Layout'] = layout
                tables.append(table)

        else:
            raise ValueError(f"Unsupported SQL flavor: {flavor}")

    except Exception as e:
        raise RuntimeError(f"Error generating schema: {str(e)}")

    return {
        'Server_Name': '',
        'Server_Description': '',
        'SQL_Flavor': flavor.capitalize(),
        'Tables': tables
    }


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
			"Name": "Table_1_Name",
			"Description": "Table 1 Description",
			"Layout": [
				{
					"Name": "Field_1_Name",
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
					"Name": "Field_2_Name",
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
			"Name": "Table_2_Name",
			"Description": "Table 2 Description",
			"Layout": [
				{
					"Name": "Field_1_Name",
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
					"Name": "Field_2_Name",
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
					"Name": "Field_3_Name",
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
