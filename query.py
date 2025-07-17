import os
from collections import defaultdict
from dotenv import load_dotenv

from Helpers import Prompter, Database


class SmartSQL:
	def __init__(self, tableLayout: dict[str], serverDescr: str = "", envPath: str = 'env_data.env', debug: bool = False, SQLflavor: str = 'Oracle SQL', **kwargs) -> None:
		"""
		Create an instance of the SmartSQL class to create and run queries
		
		Either create a 'env_data.env' (or whatever environment file specified) file with environment variables or pass as an argument to this function
  
		Args:
			tableLayout (dict[str]): A dictionary with key (table name) and value (description of what it represents and an explanation of its contents) for the model to understand what each table is for.
			envPath (str): Path to the .env file storing the connection string and API key(Optional)
			debug (bool): Whether to enable development mode. Will essentially output information and ask for confirmation before executing SQL queries.
			SQLflavor (str): Ability for users to specify which SQL 'flavor' they're using, i.e PostgreSQL or OracleSQL.
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
		self.tables = tableLayout

		with open('./tables/order_general_info.sql', 'r') as file:
			self.tables['order_general_info'] = file.read()		

		# Set other attributes
		self.debug = debug
		self.SQLflavor = SQLflavor



	def query(self, query: str, table: list[str] = None) -> list:
		"""
		Given query and table will execute database

		Args:
			query (str): Natural language prompt of what the user wants the model to do
			table (list[str]): References to keys of the tableLayout dictionary so the model can understand which tables to reference. If None, default passes all
		"""

		# Set prompt
		if table != None:
			basePrompt = f"""Using {self.SQLflavor}, help give solely SQL code to complete the query from the user, connecting to the table(s) named {', '.join(table)}. 

Do not output anything other than SQL code. The following is the layout/description for each table:\n{'\n\n'.join([f'{i}: {self.tables[i]}'] for i in table)}"""

		# If table description not provided, give all tables and let AI decide which to use/connect to
		else:
			basePrompt = f"""Using {self.SQLflavor}, help give solely SQL code to complete the query from the user. 

Do not output anything other than SQL code. The following is the layout/description for each table in the full database:\n{'\n\n'.join([f'{tableName}: {description}'] for tableName, description in self.tables.items())}"""

		# Return SQL prompt from AI
		result = self.ai.prompt(basePrompt, query)

		# If in debug mode, ask before immediately executing code
		if self.debug:
			print(result)
			if 'y' not in input("\nExecute? [Y/N] ").lower():
				return
		
		# Execute SQL code and return value/list/result
		return self.db.execute(result)
