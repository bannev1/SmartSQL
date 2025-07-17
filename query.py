import os
import json
from collections import defaultdict
from dotenv import load_dotenv

from Helpers import Prompter, Database
from settingsManager import findTable


class SmartSQL:
	def __init__(self, settings: dict, envPath: str = 'env_data.env', debug: bool = False, **kwargs) -> None:
		"""
		Create an instance of the SmartSQL class to create and run queries
		
		Either create a 'env_data.env' (or whatever environment file specified) file with environment variables or pass as an argument to this function
  
		Args:
			settings (dict): A dictionary corresponding to the structure of settings.json. See the README or settingsManager.py for more information.
			envPath (str): Path to the .env file storing the connection string and API key(Optional)
			debug (bool): Whether to enable development mode. Will essentially output information and ask for confirmation before executing SQL queries.
		"""

		kwargs = defaultdict(kwargs, str)

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
		self.debug = debug
		self.SQLflavor = settings['SQL_Flavor']
		self.name = settings['Server_Name']
		self.description = settings['Server_Description']



	def query(self, query: str, table: list[str] = None) -> list:
		"""
		Given query and table will execute database

		Args:
			query (str): Natural language prompt of what the user wants the model to do
			table (list[str]): References to keys of the tableLayout dictionary so the model can understand which tables to reference. If None, default passes all
		"""

		# Base explanation to AI for prompt
		serverExplanation = f"My database {self.name} is {self.description}. I am using {self.SQLflavor}. Help give solely SQL code to complete the query from the user. Do not output anything other than SQL code.\n"
		
		# Set conditional part of prompt
		if table != None:
			tables = [findTable(self.settings, i) for i in table]
			basePrompt = f"Make sure to connect, if necessary for the task, to the table(s) named {', '.join(table)}. The following is the layout/description for each table:\n{'\n\n'.join(json.dumps(i, indent='\t') for i in tables)}"

		# If table description not provided, give all tables/full structure and let AI decide which to use/connect to
		else:
			basePrompt = f"The following is the structure of the full database:\n{json.dumps(self.settings, indent='\t')}"

		# Return SQL prompt from AI
		result = self.ai.prompt(serverExplanation + basePrompt, query)

		# If in debug mode, ask before immediately executing code
		if self.debug:
			print(result)
			if 'y' not in input("\nExecute? [Y/N] ").lower():
				return
		
		# Execute SQL code and return value/list/result
		return self.db.execute(result)
