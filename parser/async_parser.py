import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS, URL_MAIN
import re
from urllib.parse import urljoin


urls = {
        "data": []
    }


async def get_page_data(url, session_aiohttp):
    response = await session_aiohttp.get(url)
    html = await response.text()

    soup = BeautifulSoup(html, features="lxml")

    pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
    pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    date = soup.find_all(string=pattern_date)[:10]

    for idx, link in enumerate(soup.find_all("a", href=pattern)):
        if int(date[idx][6:]) == 2023:
            print("Последняя Страница спаршена")
            print("Конец")
            print(urls)
            return
        urls["data"].append({
            "urls": link.get("href"),
            "date": (date[idx])
        })
    
    print("Страница спаршена")
    # Тут у нас url следующей страницы
    next_page_tag = soup.select_one("li.bx-pag-next a")
    if next_page_tag:
        next_page = next_page_tag.get("href")
        URL = urljoin(URL_MAIN, next_page)
        return URL


async def get_urls(url):
    async with aiohttp.ClientSession() as session_aiohttp:
        pages_to_process = [url]

        while pages_to_process:
            current_url = pages_to_process.pop(0)
            next_page = await get_page_data(url=current_url, session_aiohttp=session_aiohttp)
            if next_page:
                pages_to_process.append(next_page)


async def main():
    await get_urls(URL_WITH_RESULTS)

if __name__ == "__main__":
    asyncio.run(main())