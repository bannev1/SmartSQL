import oracledb


# NOTE: If using different database provider, please modify this class as fit

class Database:
	def __init__(self, connection: dict[str]) -> None:
		"""
		Class to manage database, provided connection details

		Args:
			connection (dict[str]): Dictionary of strings containing properties of database connection string
		
		### Example Structure of `connection`:

		```
		{
			"DB_USER" : "Username",
			"DB_PASSWORD" : "Password",
			"DB_DSN" : "dbhost.example.com/mydb"
		}
		```
		"""

		self.connect = lambda: oracledb.connect(
			user= connection['DB_USER'],
			password= connection['DB_PASSWORD'],
			dsn= connection['DB_DSN']
		)

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
		except oracledb.InterfaceError: # No result needed – .fetchall() fails
			result = []

		# Close connections
		cursor.close()
		connection.close()

		return result
