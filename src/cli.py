# IMPORT
import os
import src.settingsManager as settingsManager
from src import SmartSQL

# PREFERENCES
preferences = {
    'ENV_PATH': "./env_data.env",
    'SETTINGS_JSON': "./settings.json",
    'SQL_FILE': "./sqlReference.sql",
    'DATABASE_PROVIDER': "",
    'SQL_FLAVOR': ''
}

def get_user_input(prompt, default=None, options=None):
    """Helper function to get user input with default values and validation"""
    while True:
        response = input(f"{prompt} [{default}] " if default else prompt).strip()
        if not response and default:
            return default
        if not options or response.lower() in options:
            return response
        print(f"Invalid input. Please choose from: {', '.join(options)}")

# Get file paths
preferences['ENV_PATH'] = get_user_input("Path to .env file:", default=preferences['ENV_PATH'])
preferences['SETTINGS_JSON'] = get_user_input("Path to settings JSON:", default=preferences['SETTINGS_JSON'])
preferences['SQL_FILE'] = get_user_input("Path to SQL reference file:", default=preferences['SQL_FILE'])

# Select SQL flavor
print("\nSelect SQL flavor:")
print("  [1] PostgreSQL")
print("  [2] Oracle Database")

preferences['SQL_FLAVOR'] = get_user_input(
    "Enter flavor number [1/2]:", 
    options=['1', '2']
)

if preferences['SQL_FLAVOR'] == '1':
    preferences['SQL_FLAVOR'] = 'postgres'
    preferences['DATABASE_PROVIDER'] = 'PostgreSQL'
else:
    preferences['SQL_FLAVOR'] = 'oracle'
    preferences['DATABASE_PROVIDER'] = 'Oracle Database'

print(f"\nSelected: {preferences['DATABASE_PROVIDER']}\n")

# Settings creation flow
create_settings = get_user_input("Create settings dictionary? [Y/N]:", options=['y', 'n'])
settings = None

if create_settings.lower() == 'y':
    print("\nCreate settings from:")
    print("  [1] SQL file with CREATE TABLE statements")
    print("  [2] Direct database connection")
    
    source = get_user_input("Select source [1/2]:", options=['1', '2'])
    
    if source == '1':
        if not os.path.exists(preferences['SQL_FILE']):
            print(f"\nError: SQL file not found at {preferences['SQL_FILE']}")
            print("Please create the file or specify a different path.")
            exit(1)
            
        with open(preferences['SQL_FILE'], 'r') as file:
            sql_content = file.read()
            settings = settingsManager.settingsWithAIPath(
                f"Using {preferences['DATABASE_PROVIDER']}\n\n" + sql_content,
                preferences['ENV_PATH']
            )
            settingsManager.exportSettings(settings, preferences['SETTINGS_JSON'])
            print(f"\nSettings created and saved to {preferences['SETTINGS_JSON']}")
    
    else:  # Direct database connection
        print("\nDatabase connection setup:")
        db_config = {
            'host': get_user_input("Database host:"),
            'port': get_user_input("Database port:"),
            'user': get_user_input("Database user:"),
            'password': get_user_input("Database password:"),
            'database': get_user_input("Database name:"),
        }
        
        settings = settingsManager.settingsFromDB(
            preferences['SQL_FLAVOR'], 
            db_config
        )
        settingsManager.exportSettings(settings, preferences['SETTINGS_JSON'])
        print(f"\nSettings created and saved to {preferences['SETTINGS_JSON']}")

else:  # Load existing settings
    if not os.path.exists(preferences['SETTINGS_JSON']):
        print(f"\nError: Settings file not found at {preferences['SETTINGS_JSON']}")
        exit(1)
        
    settings = settingsManager.parseSettings(preferences['SETTINGS_JSON'])
    print("\nLoaded existing settings")

# Initialize SmartSQL
print("\nInitializing SmartSQL...")
exp = SmartSQL(
    settings, 
    preferences['SQL_FLAVOR'], 
    envPath=preferences['ENV_PATH'], 
    confirmExecute=True
)

# For validation
allTables = settingsManager.getAllTables(settings)
print(f"\nFound {len(allTables)} tables in settings")

# Query loop
print("\nStarting query interface. Type 'exit' to quit at any time.")
while True:
    try:
        # Get query
        query = input("\nPlease make a request: ").strip()
        if query.lower() in ['exit', 'quit']:
            break
            
        # Table selection
        tables = None
        specify_tables = get_user_input("Specify tables? [Y/N]:", options=['y', 'n'])
        
        if specify_tables.lower() == 'y':
            print(f"Available tables: {', '.join(allTables)}")
            table_input = input("Enter tables (comma separated): ").strip()
            selected_tables = [t.strip() for t in table_input.split(',') if t.strip()]
            
            # Validate tables
            valid_tables = [t for t in selected_tables if t in allTables]
            invalid_tables = [t for t in selected_tables if t not in allTables]
            
            if invalid_tables:
                print(f"Warning: Ignoring invalid tables: {', '.join(invalid_tables)}")
                
            if valid_tables:
                tables = valid_tables
                print(f"Using tables: {', '.join(valid_tables)}")
            else:
                print("No valid tables selected. Using all available tables.")
        
        # Execute query
        print("\nProcessing query...")
        result = exp.query(query, tables)
        
        # Output result
        if result:
            print(f"\nResult:\n{result}")
        else:
            print("\nNo results returned")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        continue
    except Exception as e:
        print(f"\nError: {str(e)}")
        continue

print("\nExiting SmartSQL. Goodbye!")
