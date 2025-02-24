import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS, URL_MAIN
import re
from urllib.parse import urljoin
from time import time
from exceptions import YearComplited


urls = {
        "data": []
    }


def parse_tags(date, links):
    for idx, link in enumerate(links):
        if int(date[idx][6:]) == 2023:
            print("Последняя Страница спаршена")
            print("Конец")
            print(urls)
            raise YearComplited
        urls["data"].append({
            "urls": link.get("href"),
            "date": (date[idx])
        })
    print("Страница спаршена")


async def get_urls(url, session_aiohttp):
    response = await session_aiohttp.get(url)
    html = await response.text()

    soup = BeautifulSoup(html, features="lxml")

    pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
    pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    date = soup.find_all(string=pattern_date)[:10]
    links = soup.find_all("a", href=pattern)

    try:
        parse_tags(date, links)
    except YearComplited:
        return

    next_page_tag = soup.select_one("li.bx-pag-next a")
    if next_page_tag:
        next_page = next_page_tag.get("href")
        URL = urljoin(URL_MAIN, next_page)
        await asyncio.create_task(get_urls(URL, session_aiohttp))


async def main():
    async with aiohttp.ClientSession() as session_aiohttp:
        await get_urls(URL_WITH_RESULTS, session_aiohttp)


if __name__ == "__main__":
    time0 = time()
    asyncio.run(main())
    time_ = round((time() - time0), 2)
    print(time_)