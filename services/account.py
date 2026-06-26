import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY")

HEADERS = {
    "Authorization": API_KEY
}

BASE_URL = "https://api.henrikdev.xyz"


async def get_account(name: str, tag: str):

    url = f"{BASE_URL}/valorant/v1/account/{name}/{tag}"

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        async with session.get(url) as response:

            if response.status != 200:
                return None

            return await response.json()