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
from db.config import AsyncSessionLocal
import logging
from sqlalchemy.exc import SQLAlchemyError
from pandas.core.frame import DataFrame
from .configs import configure_argument_parser, configure_logging

BASE_DIR = Path(__file__).resolve().parent.parent


async def get_urls(url, session_aiohttp: aiohttp.ClientSession, queue: asyncio.Queue, year_stop: int):
    """
    Получаем страницу для парсинга, 'варим суп', получаем теги: дат, ссылок на файлы, следующей страницы
      url - адресс страницы для парсинга
      session_aiohttp - aiohttp.ClientSession сессия
      year_stop - год давности файлов, передается в parse_tags
    """
    try:
        response = await session_aiohttp.get(url)
        html = await response.text()

        soup = BeautifulSoup(html, features="lxml")

        pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
        pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

        date = soup.find_all(string=pattern_date)[:10]
        links = soup.find_all("a", href=pattern)

        try:
            await parse_tags(date, links, queue, year_stop)
        except YearComplited:
            logging.info("Ссылки на файлы получены. Стоп по году.")
            return

        next_page_tag = soup.select_one("li.bx-pag-next a")
        if next_page_tag:
            next_page = next_page_tag.get("href")
            URL = urljoin(URL_MAIN, next_page)

            await asyncio.create_task(get_urls(URL, session_aiohttp, queue, year_stop))
        else:
            logging.info("Ссылки на файлы получены. Стоп - больше нет страниц.")
            return

    except aiohttp.ClientError as e:
        logging.exception(f"Ошибка aiohttp при получении {url}: {e}")
    except asyncio.TimeoutError:
        logging.exception(f"Тайм-аут при получении {url}")
    except AttributeError as e:
        logging.exception(f"Ошибка BeautifulSoup при парсинге {url}: {e}")
    except re.error as e:
        logging.exception(f"Ошибка регулярного выражения при парсинге {url}: {e}")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при получении {url}: {e}")


async def parse_tags(date: list, links: list, queue: asyncio.Queue, year_stop: int):
    """
    Достаем url для скачивания файла
      date - спиcок дат на странице
      links - список тега ссылок на файлы
      year_stop - год давности файлов
    """
    try:
        for idx, link in enumerate(links):
            if int(date[idx][6:]) == year_stop:
                raise YearComplited
            await queue.put(link.get("href"))
    except YearComplited:
        raise
    except ValueError:
        logging.exception(f"Некорректная дата {date[idx]}. Не было приведено к целому числу.")
    except IndexError:
        logging.exception("Ошибка: Индексы в списках date и links не совпадают.")


async def download_xml(url, session_aiohttp: aiohttp.ClientSession, queue: asyncio.Queue) -> str:
    """Скачиваем файлы по url"""
    download = BASE_DIR / 'download'
    try:
        download.mkdir(exist_ok=True)
        name = url.split('/')[-1].split('?')[0]
        filename = download / name
        url_full = urljoin(URL_MAIN, url)
        try:
            async with session_aiohttp.get(url_full) as response:
                if response.status == HTTPStatus.OK:
                    content = await response.read()
                    with open(filename, mode='wb') as f:
                        f.write(content)
                    queue.task_done()
                    return str(filename)
                else:
                    queue.task_done()
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка aiohttp при скачивании {url_full}: {e}")
            queue.task_done()
            return None
        except asyncio.TimeoutError:
            logging.error(f"Тайм-аут при скачивании {url_full}")
            queue.task_done()
            return None
    except (OSError, FileNotFoundError, PermissionError) as e:
        logging.error(f"Ошибка файловой системы при скачивании {url}: {e}")
        queue.task_done()
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при скачивании {url}: {e}")
        queue.task_done()
        return None


async def parse_file(file_path: str):
    """
    Достаем данные из файла для записи в БД
      file_path - путь к файлу
    """
    try:
        pattern_date = r'oil_xls_(\d{8})'
        match_date = re.search(pattern_date, file_path)
        if not match_date:
            logging.info(f"Не удалось извлечь дату из имени файла {file_path}")
            return None
        date_doc = match_date.group(1)
        date = datetime.strptime(date_doc, '%Y%m%d').date()
        
        df = pd.read_excel(file_path, header=None)
        mathed_row = df[df.apply(lambda row: row.astype(str).str.contains('Метрическая тонна').any(), axis=1)].index
        if mathed_row.empty:
            logging.info(f"Ошибка: 'Метрическая тонна' не найдена в файле {file_path}")
            return None
        header_row = mathed_row[0]

        res_df = pd.read_excel(file_path, header=header_row + 2)
        return date, res_df
    
    except Exception as e:
        logging.exception(f"Ошибка при парсинге файлов в {file_path}: {e}", stack_info=True)


async def save_data_to_db(data):
    """Открываем сессии для работы с БД"""
    async with AsyncSessionLocal() as session:
        await save_in_db(data[0], data[1], session)


async def save_in_db(date: datetime.date, res_df: DataFrame, session):
    """
    Создаем объект SpimexTradingResult и его сохраняем в базу данных
      date - дата файла
      res_df - DataFrame c данными из таблицы(файла)
    """
    try:
        for index in range(100000):
            rows = res_df.iloc[index].to_list()
            if rows[1] in ('Итого:', 'Итого: ', ' Итого:', 'Итого по секции:'):
                break
            if pd.isna(rows[4]) or pd.isna(rows[14]) or pd.isna(rows[5]):
                continue
            if rows[14] == '-':
                continue
            new_oil = SpimexTradingResult(
                exchange_product_id=str(rows[1]),
                exchange_product_name=str(rows[2]),
                oil_id=str(rows[1][:4]),
                delivery_basis_id=str(rows[1][4:7]),
                delivery_basis_name=str(rows[3]),
                delivery_type_id=str(rows[1][-1]),
                volume=int(rows[4]) if rows[4] != "-" else 0,
                total=int(rows[5]) if rows[5] != "-" else 0,
                count=int(rows[14]) if rows[14] != "-" else 0,
                date=date
            )
            session.add(new_oil)
        await session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Ошибка SQLAlchemy при сохранении объекта в базу данных: {e}")
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при сохранении объекта в базу данных {e}")


async def main(year_stop):
    queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session_aiohttp:

        await get_urls(URL_WITH_RESULTS, session_aiohttp, queue, year_stop)

        tasks = []
        for _ in range(queue.qsize()):
            url = await queue.get()
            task = asyncio.create_task(download_xml(url, session_aiohttp, queue))
            tasks.append(task)
            
        download_files = await asyncio.gather(*tasks)

        await queue.join()

        tasks_files = []
        for file_path in download_files:
            tasks_files.append(asyncio.create_task(parse_file(file_path)))

        data_to_save = await asyncio.gather(*tasks_files)

        tasks_save = []
        for data in data_to_save:
            if data is None:
                continue
            tasks_save.append(asyncio.create_task(save_data_to_db(data)))
        await asyncio.gather(*tasks_save)
        

if __name__ == "__main__":
    configure_logging()
    logging.info("Парсер запущен! Введите год до которого требуется спарсить данные")
    arg_parse = configure_argument_parser()
    args = arg_parse.parse_args()
    year_stop = args.year_stop
    
    logging.info(f"Данные будут загружаться до {year_stop} года.")

    time0 = time()
    logging.info("Начался парсинг..")
    asyncio.run(main(year_stop))
    time_ = round((time() - time0), 2)
    logging.info(f"Парсинг завершен время затраченое на работу {time_}")