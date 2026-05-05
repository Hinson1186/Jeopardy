import os
import requests
from dotenv import load_dotenv
from game_models import Clue

class AzureClueService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("AZURE_API_KEY")
        self.endpoint = os.getenv("AZURE_ENDPOINT_URL")