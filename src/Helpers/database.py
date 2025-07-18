# NOTE: If using different database provider, please modify this class as fit

class Database:
	def __init__(self, connection: dict[str], flavor: str) -> None:
		"""
		Class to manage database, provided connection details

		Args:
			connection (dict[str]): Dictionary of strings containing properties of database connection string
			flavor (str): Type of SQL - Currently only 'oracle' or 'postgres' supported
		
		### Example Structure of `connection` for 'oracle':

		```
		{
			"DB_USER" : "Username",
			"DB_PASSWORD" : "Password",
			"DB_DSN" : "dbhost.example.com/mydb"
		}
		```

		### Example Structure of `connection` for 'oracle':

		```
		{
			"DB_USER" : "Username",
			"DB_PASSWORD" : "Password",
			"DB_NAME" : "Name",
			"DB_HOST": "host.com",
			"DB_PORT": "0000"
		}
		```
		"""

		match flavor:
			case 'oracle':
				import oracledb
				self.connect = lambda: oracledb.connect(
					user= connection['DB_USER'],
					password= connection['DB_PASSWORD'],
					dsn= connection['DB_DSN']
				)

			case 'postgres':
				import psycopg2
				self.connect = lambda: psycopg2.connect(
					user= connection['DB_USER'],
					password= connection['DB_PASSWORD'],
					dbname= connection['DB_NAME'],
					host= connection['DB_HOST'],
					port= connection['DB_PORT']
				)
			
			case _:
				raise ValueError("Only 'oracle' and 'postgres' flavors available at the moment.")


	def execute(self, code: str) -> list:
		"""
		Executes SQL code given with Oracle DB
		"""

		# Connect to DB
		connection = self.connect()
		cursor = connection.cursor()

		# Run SQL
		cursor.execute(code)

		try:
			result = cursor.fetchall()
		except Exception: # No result needed – .fetchall() fails
			result = []

		# Close connections
		cursor.close()
		connection.close()

		return result
