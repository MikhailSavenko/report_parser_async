import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS, URL_MAIN
import re


urls = {
        "data": [
        ]
    }


async def get_urls():
    
    async with aiohttp.ClientSession() as session_aiohttp:
        
        response = await session_aiohttp.get(URL_WITH_RESULTS)
        html = await response.text()
        
        soup = BeautifulSoup(html, features="lxml")
        
        pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
        pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")
          
        date = soup.find_all(string=pattern_date)[:10]
        
        for idx, link in enumerate(soup.find_all("a", href=pattern)):
            if int(date[idx][6:]) == 2024:
                break
        
            urls["data"].append({
                "urls": link.get("href"),
                "date": (date[idx])
            })
        # Тут у нас url следующей страницы  
        next_page = soup.select_one("li.bx-pag-next a").get("href")

        print(urls)
        #
        # print(next_page)
        # if next_page
        
        # print(date)



async def main():
    pass

if __name__ == "__main__":
    asyncio.run(get_urls())