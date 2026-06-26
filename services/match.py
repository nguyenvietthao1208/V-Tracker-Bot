import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY")

HEADERS = {
    "Authorization": API_KEY
}

BASE_URL = "https://api.henrikdev.xyz"


async def get_matches(region, name, tag, size=5):

    url = f"{BASE_URL}/valorant/v4/matches/{region}/pc/{name}/{tag}?size={size}"

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        async with session.get(url) as response:

            if response.status != 200:
                print(await response.text())
                return None

            return await response.json()