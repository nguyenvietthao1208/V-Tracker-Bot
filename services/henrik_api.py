import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY")

BASE_URL = "https://api.henrikdev.xyz"


async def get_account(name: str, tag: str):
    headers = {
        "Authorization": API_KEY
    }

    url = f"{BASE_URL}/valorant/v1/account/{name}/{tag}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            if response.status != 200:
                print(await response.text())
                return None

            return await response.json()