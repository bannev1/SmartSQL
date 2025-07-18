# Run this file from the root of this directory

# IMPORT
import os

import src.settingsManager as settingsManager
from src import SmartSQL


# PREFERENCES
ENV_PATH = "./env_data.env"
SETTINGS_JSON = "./testSettings.json"

# If need to set settings
if 'y' in input('Set settings/server information? [Y/N] ').lower():
	# Get settings from DB directly (multiple ways to approach this)
	settings = settingsManager.settingsFromDBPath(ENV_PATH)

	# Export for modification
	settingsManager.exportSettings(settings, exportPath=SETTINGS_JSON)

	# Wait for user to go to SETTINGS_JSON and update descriptions/names
	print(f"Please modify newly updated {SETTINGS_JSON} and add relevant descriptions.")

	while 'y' not in input(f'Have you updated {SETTINGS_JSON} with correct information? [Y/N] ').lower():
		print(f"Please modify newly updated {SETTINGS_JSON} and add relevant descriptions.\n")

# Otherwise grab settings
else:
	settings = settingsManager.parseSettings(SETTINGS_JSON)


# START QUERIES
# Create instance of SmartSQL class
exp = SmartSQL(settings, envPath=ENV_PATH)


# For validation later, get all tables available
allTables = settingsManager.getAllTables(settings)

while True:
	os.system('clear')

	# Get query
	query = input('Please make a request: ')

	tables = None

	if 'y' in input('Do you know which tables you need to access specifically? [Y/N] ').lower():
		tables = [table for table in input('Please enter the tables you need separated by a comma (Capitalization is important): ').strip() if table in allTables]

		print(f"Tables referenced which are available in database: {', '.join(tables)}")

	# Execute code
	result = exp.query(query, tables if tables == None or len(tables) > 0 else None)

	# Output result
	print(f"Result:\n{result}")

	# Exit if user specifies
	if 'y' not in input('Do you wish to make another query? [Y/N] ').lower():
		break
