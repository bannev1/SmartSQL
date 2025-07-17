import os
import json
from collections import defaultdict
from dotenv import load_dotenv

from Helpers import Prompter, Database
from settingsManager import findTable


class SmartSQL:
	def __init__(self, settings: dict, envPath: str = 'env_data.env', confirmExecute: bool = True, **kwargs) -> None:
		"""
		Create an instance of the SmartSQL class to create and run queries
		
		Either create a 'env_data.env' (or whatever environment file specified) file with environment variables or pass as an argument to this function
  
		Args:
			settings (dict): A dictionary corresponding to the structure of settings.json. See the README or settingsManager.py for more information.
			envPath (str): Path to the .env file storing the connection string and API key(Optional)
			confirmExecute (bool): Will essentially decide if need to output information and ask for confirmation before executing SQL queries.
		"""

		kwargs = defaultdict(str, kwargs)

		load_dotenv(envPath)

		# Fetch all keys required
		keys = [
			"AZURE_OPENAI_API_KEY",
			"AZURE_OPENAI_API_VERSION",
			"AZURE_OPENAI_ENDPOINT",
			"AZURE_OPENAI_DEPLOYMENT_NAME",
			"DB_USER",
			"DB_PASSWORD",
			"DB_DSN"
		]

		# Generate key dictionary
		apiKeys = {key: os.getenv(key, kwargs[key]) for key in keys}

		# Set up connections to AI and database
		self.ai = Prompter(apiKeys)
		self.db = Database(apiKeys)

		# Set up tables
		self.settings = settings	

		# Set other attributes
		self.debug = confirmExecute
		self.SQLflavor = settings['SQL_Flavor']
		self.name = settings['Server_Name']
		self.description = settings['Server_Description']



	def query(self, query: str, table: list[str] = None, withBacklog: bool = True, confirmExecute: bool = None) -> list:
		"""
		Given query and table will execute database

		Args:
			query (str): Natural language prompt of what the user wants the model to do
			table (list[str]): References to keys of the tableLayout dictionary so the model can understand which tables to reference. If None, default passes all
			withBacklog (bool): If needs to maintain history of past changes
			confirmExecute (bool): Whether to override original confirmExecute attribute
		"""

		# Base explanation to AI for prompt
		serverExplanation = f"My database {self.name} is {self.description}. I am using {self.SQLflavor}. Help give solely SQL code to complete the query from the user. Do not output anything other than SQL code and do NOT put it in a code block and do NOT add comments. Just raw text.\n"

		# Set conditional part of prompt
		if table != None:
			tables = [findTable(self.settings, i) for i in table]
			basePrompt = f"Make sure to connect, if necessary for the task, to the table(s) named {', '.join(table)}. The following is the layout/description for each table:\n{'\n\n'.join(json.dumps(i, indent='\t') for i in tables)}"

		# If table description not provided, give all tables/full structure and let AI decide which to use/connect to
		else:
			basePrompt = f"The following is the structure of the full database:\n{json.dumps(self.settings, indent='\t')}"

		# Check if need to include command history
		if withBacklog:
			if len(self.ai.backlog) > 0:
				basePrompt += f"\n\nPlease note that the following commands have been executed to the database description aforementioned, meaning you need to consider the following changes/commands to have taken effect before writing your SQL code:\n{'\n'.join(self.ai.backlog)}"

		# Return SQL prompt from AI
		result = self.ai.prompt(serverExplanation + basePrompt, query)

		# If in confirmExecute mode, ask before immediately executing code
		if (self.debug and confirmExecute == None) or confirmExecute:
			print(result)
			if 'y' not in input("\nExecute? [Y/N] ").lower():
				self.ai.backlog.pop() # Remove record from being included in backlog
				return
		
		# Execute SQL code and return value/list/result
		result = self.db.execute(result)

		# If no result, return empty list
		if result == None:
			return []
		
		return result

	def updateSettings(self, newSettings: dict) -> None:
		"""
		Updates settings and clears backlog

		Args:
			newSettings (dict): New settings/server configuration to replace old one
		"""

		# Updating settings meaning backlog is no longer accurate
		self.settings = newSettings
		self.ai.clearBacklog()
