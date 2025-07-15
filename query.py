import os
from collections import defaultdict
from dotenv import load_dotenv
from openai import AzureOpenAI
import oracledb

class SmartSQL:
	_instance = None

	def __new__(cls, *args, **kwargs):
		"""Ensure only one instance of the class is created (Singleton)."""
		if not cls._instance:
			cls._instance = super(SmartSQL, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self, envPath: str = 'env_data.env', **kwargs) -> None:
		"""
		Create an instance of the SmartSQL class to create and run queries
		
		Either create a 'env_data.env' (or whatever environment file specified) file with environment variables or pass as an argument to this function
		"""

		kwargs = defaultdict(kwargs, str)

		load_dotenv(envPath)

		# Set up client
		self.client = AzureOpenAI(
			api_key= os.getenv("AZURE_OPENAI_API_KEY", kwargs['AZURE_OPENAI_API_KEY']),
			api_version= os.getenv("AZURE_OPENAI_API_VERSION", kwargs['AZURE_OPENAI_API_VERSION']),
			azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT", kwargs['AZURE_OPENAI_ENDPOINT'])
		)

		self.deploymentName = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", kwargs['AZURE_OPENAI_DEPLOYMENT_NAME'])

		self.tables = {
			"order_general_info": ""
		}

		with open('./tables/order_general_info.sql', 'r') as file:
			self.tables['order_general_info'] = file.read()

		# Connect DB
		self.connect = lambda: oracledb.connect(
			user= os.getenv("DB_USER", kwargs['DB_USER']),
			password= os.getenv("DB_PASSWORD", kwargs['DB_PASSWORD']),
			dsn= os.getenv("DB_DSN", kwargs['DB_DSN'])
		)


	def query(self, table: str, query: str) -> list:
		"""
		Given query and table will execute database
		"""

		BASEPROMPT = f"""Using the Oracle SQL Database, help give solely SQL code for table {table}. Do not output anything other than SQL code. The following is the layout:\n{self.tables[table]}"""

		# Prompt GPT
		response = self.client.chat.completions.create(
			model = self.deploymentName,
			messages = [
					{
						"role": "system", "content": BASEPROMPT,
						"role": "user", "content": query
					}
				],
			temperature = 0.8,
			max_tokens = 800
		)

		output = response.choices[0].message.content
		
		# Run SQL
		connection = self.connect()
		cursor = connection.cursor()

		cursor.execute(output)
		try:
			result = cursor.fetchall()
		except oracledb.InterfaceError:
			result = []

		cursor.close()
		connection.close()

		return result
