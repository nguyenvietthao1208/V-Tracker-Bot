import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY")

HEADERS = {
    "Authorization": API_KEY
}

BASE_URL = "https://api.henrikdev.xyz"


async def get_matches(name: str, tag: str):
    pass