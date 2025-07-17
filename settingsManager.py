import json
import os
from dotenv import load_dotenv

from Helpers import Database, Prompter


# SETTINGS OBJECT REPRESENTATION
class Settings:
    def __init__(self, settings: dict) -> None:
        """
        Set settings. Also makes sure all values set, otherwise Key_Error

        Args:
            settings (dict): Settings
        """

        # Set attributes
        self.settings = settings
        self.serverName = settings['Server_Name']
        self.serverDescription
    

    def export(self, exportPath: str = "./settings.json") -> dict:
        """
        Export settings to JSON file as a dictionary

        Args:
            exportPath (str): Path to export JSON file to
        """

        # Get settings
        settings = self.settings

        # Open and export
        with open(exportPath, 'r+') as file:
            json.dump(settings, file)

        return settings



# PROCESSORS

def settingsFromDB(envPath: str = 'env_data.env') -> Settings:
    """
    Generate settings from database directly with AI

    Args:
        envPath (str): Environment variables .env file path to process connection string
    """

    # Load environment variables
    load_dotenv(envPath)

    # Process
    return settingsFromDB(
        {
            "DB_USER": os.getenv('DB_USER'),
            "DB_PASSWORD": os.getenv('DB_PASSWORD'),
            "DB_DSN": os.getenv('DB_DSN')
        }
    )

def settingsFromDB(connection: dict[str]) -> Settings:
    """
    Generate settings from database directly with AI

    Args:
        connection (dict[str]): Connection properties. See README for exact structure
    """

    # Connect DB
    db = Database(connection)

    # Get all tables
    db.execute("""

""")


def parseSettings(settingsPath: str) -> Settings:
    """
    Parse JSON path to get settings
    """

    return Settings(json.loads(settingsPath))
