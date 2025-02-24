import aiohttp
from bs4 import BeautifulSoup
import asyncio
from .constants import URL_WITH_RESULTS, URL_MAIN
import re
from urllib.parse import urljoin
from time import time
from .exceptions import YearComplited
from pathlib import Path
from http import HTTPStatus
import pandas as pd
from datetime import datetime
from db.models import SpimexTradingResult
from db.config import get_async_session


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


async def parse_file(file_path, session):
    # Получим дату 
    pattern_date = r'oil_xls_(\d{8})'
    match_date = re.search(pattern_date, file_path)
    date_doc = match_date.group(1)
    
    df = pd.read_excel(file_path, header=None)
    header_row = df[df.apply(lambda row: row.astype(str).str.contains('Метрическая тонна').any(), axis=1)].index[0]
    res_df = pd.read_excel(file_path, header=header_row+2)
    date = datetime.strptime(date_doc, '%Y%m%d').date()
    
    for index in range(100000):
        rows = res_df.iloc[index].to_list()
        if rows[1] in ('Итого:', 'Итого: ', ' Итого:', 'Итого по секции:'):
            break
        if rows[14] == '-':
            continue
        new_oil = SpimexTradingResult(
            exchange_product_id=rows[1],
            exchange_product_name=rows[2],
            oil_id=rows[1][:4],
            delivery_basis_id=rows[1][4:7],
            delivery_basis_name=rows[3],
            delivery_type_id=rows[1][-1],
            volume=rows[4],
            total=rows[5],
            count=rows[14],
            date=date
        )
        await session.add(new_oil)
    await session.commit()
    return new_oil


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
        
        download_files = await asyncio.gather(*tasks)

        async with get_async_session() as session:
            tasks = [asyncio.create_task(parse_file(file_path, session)) for file_path in download_files]

            await asyncio.gather(*tasks)

if __name__ == "__main__":
    time0 = time()
    asyncio.run(main())
    time_ = round((time() - time0), 2)
    print(time_)