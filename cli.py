# IMPORT
import src.settingsManager as settingsManager
from src import SmartSQL


# PREFERENCES
ENV_PATH = "./env_data.env"
SETTINGS_JSON = "./settings.json"
SQL_FILE = "./sqlReference.sql"
DATABASE_PROVIDER = "Oracle Database"

# If need to set settings
if 'y' in input('Set settings? [Y/N] ').lower(): 
	with open(SQL_FILE, 'r+') as file:
		settings = settingsManager.settingsWithAIPath(f"Using {DATABASE_PROVIDER}\n\n" + '\n'.join(file.readlines()), ENV_PATH)
		settingsManager.exportSettings(settings, SETTINGS_JSON)
else:
	settings = settingsManager.parseSettings(SETTINGS_JSON)

# START QUERIES
# Create instance of SmartSQL class
exp = SmartSQL(settings, 'postgres', envPath=ENV_PATH, confirmExecute=True)


# For validation later, get all tables available
allTables = settingsManager.getAllTables(settings)

while True:
	# Get query
	query = input('Please make a request: ')

	tables = None

	if 'y' in input('Do you know which tables you need to access specifically? [Y/N] ').lower():
		tables = [table for table in input('Please enter the tables you need separated by a comma (Capitalization is important): ').strip() if table in allTables]

		print(f"Tables referenced which are available in database: {', '.join(tables)}")

		exp.query(query, tables if tables == None or len(tables) > 0 else None)
		continue

	# Execute code
	result = exp.query(query, tables if tables == None or len(tables) > 0 else None)

	# Output result
	print(f"Result:\n{result}")

	# Exit if user specifies
	if 'y' not in input('Do you wish to make another query? [Y/N] ').lower():
		break
