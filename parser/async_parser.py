import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS, URL_MAIN
import re
from urllib.parse import urljoin


urls = {
        "data": []
    }


async def get_urls(url):

    async with aiohttp.ClientSession() as session_aiohttp:

        response = await session_aiohttp.get(url)
        html = await response.text()

        soup = BeautifulSoup(html, features="lxml")

        pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
        pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

        date = soup.find_all(string=pattern_date)[:10]

        for idx, link in enumerate(soup.find_all("a", href=pattern)):
            if int(date[idx][6:]) == 2024:
                return

            urls["data"].append({
                "urls": link.get("href"),
                "date": (date[idx])
            })
        # Тут у нас url следующей страницы
        next_page_tag = soup.select_one("li.bx-pag-next a")

        print("Страница спаршена")
        if next_page_tag:
            next_page = next_page_tag.get("href")
            URL = urljoin(URL_MAIN, next_page)
            await get_urls(URL)
            print("Конец")
            print(urls)


async def main():
    await get_urls(URL_WITH_RESULTS)

if __name__ == "__main__":
    asyncio.run(main())