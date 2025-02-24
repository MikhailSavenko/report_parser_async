import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS
import re


async def get_urls():
    urls = []
    async with aiohttp.ClientSession() as session_aiohttp:
        response = await session_aiohttp.get(URL_WITH_RESULTS)
        html = await response.text()
        
        soup = BeautifulSoup(html, features="lxml")
        
        pattern = re.compile(r'/upload/reports/oil_xls/.*\.xls')
        
        for link in soup.find_all("a", href=pattern):
            urls.append(link.get("href"))


if __name__ == "__main__":
    asyncio.run(get_urls())