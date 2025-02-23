import aiohttp
from bs4 import BeautifulSoup
import asyncio
from constants import URL_WITH_RESULTS, URL_MAIN
import re
from urllib.parse import urljoin
from time import time
from exceptions import YearComplited
from pathlib import Path
from http import HTTPStatus

BASE_DIR = Path(__file__).resolve().parent.parent

urls = []


def parse_tags(date, links):
    for idx, link in enumerate(links):
        if int(date[idx][6:]) == 2023:
            print("Последняя Страница спаршена")
            print("Конец")
            print(urls)
            raise YearComplited

        urls.append(link.get("href"))
    print("Страница спаршена")
    

async def download_xml(url, session_aiohttp):
    download = BASE_DIR / 'download'
    download.mkdir(exist_ok=True)
    name = url.split('/')[-1].split('?')[0]
    filename = download / name
    url_full = urljoin(URL_MAIN, url)

    async with session_aiohttp.get(url_full) as response:
        if response.status == HTTPStatus.OK:
            content = await response.read()
            with open(filename, mode='wb') as f:
                f.write(content)
            return filename
    return None


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

        tasks = [asyncio.create_task(download_xml(url, session_aiohttp)) for url in urls]
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    time0 = time()
    asyncio.run(main())
    time_ = round((time() - time0), 2)
    print(time_)