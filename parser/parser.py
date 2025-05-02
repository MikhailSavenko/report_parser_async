import logging
import re
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from queue import Queue
from time import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
from sqlalchemy.exc import SQLAlchemyError

from db.config import SessionLocal
from db.models import SpimexTradingResult

from .configs import configure_argument_parser, configure_logging
from .constants import URL_MAIN, URL_WITH_RESULTS
from .exceptions import YearComplited

BASE_DIR = Path(__file__).resolve().parent.parent


def get_urls(url, queue: Queue, year_stop: int):
    """
    Получаем страницу для парсинга, 'варим суп', получаем теги: дат, ссылок на файлы, следующей страницы
      url - адресс страницы для парсинга
      session_aiohttp - aiohttp.ClientSession сессия
      year_stop - год давности файлов, передается в parse_tags
    """
    try:
        response = requests.get(url)
        html = response.text

        soup = BeautifulSoup(html, features="lxml")

        pattern = re.compile(r"/upload/reports/oil_xls/.*\.xls")
        pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

        date = soup.find_all(string=pattern_date)[:10]
        links = soup.find_all("a", href=pattern)
        print(date)
        try:
            parse_tags(date, links, queue, year_stop)
        except YearComplited:
            logging.info("Ссылки на файлы получены. Стоп по году.")
            return

        next_page_tag = soup.select_one("li.bx-pag-next a")
        if next_page_tag:
            next_page = next_page_tag.get("href")
            URL = urljoin(URL_MAIN, next_page)

            get_urls(URL, queue, year_stop)
        else:
            logging.info("Ссылки на файлы получены. Стоп - больше нет страниц.")
            return

    except AttributeError as e:
        logging.exception(f"Ошибка BeautifulSoup при парсинге {url}: {e}")
    except re.error as e:
        logging.exception(f"Ошибка регулярного выражения при парсинге {url}: {e}")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при получении {url}: {e}")


def parse_tags(date: list, links: list, queue: Queue, year_stop: int):
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
            queue.put(link.get("href"))
    except YearComplited:
        raise
    except ValueError:
        logging.exception(f"Некорректная дата {date[idx]}. Не было приведено к целому числу.")
    except IndexError:
        logging.exception("Ошибка: Индексы в списках date и links не совпадают.")


def download_xml(url, queue: Queue) -> str:
    """Скачиваем файлы по url"""
    download = BASE_DIR / "download"
    try:
        download.mkdir(exist_ok=True)
        name = url.split("/")[-1].split("?")[0]
        filename = download / name
        url_full = urljoin(URL_MAIN, url)
        try:
            response = requests.get(url_full, timeout=30)
            if response.status_code == HTTPStatus.OK:
                content = response.content
                with open(filename, mode="wb") as f:
                    f.write(content)
                queue.task_done()
                return str(filename)
            else:
                queue.task_done()
                return None
        except requests.Timeout:
            logging.exception(f"Таймаут при скачивании {url_full}")
            queue.task_done()
            return None
        except requests.RequestException as e:
            logging.exception(f"Ошибка requests при скачивании {url_full}: {str(e)}")
            queue.task_done()
            return None
    except (OSError, FileNotFoundError, PermissionError) as e:
        logging.exception(f"Ошибка файловой системы при скачивании {url}: {e}")
        queue.task_done()
        return None
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при скачивании {url}: {e}")
        queue.task_done()
        return None


def parse_file(file_path: str):
    """
    Достаем данные из файла для записи в БД
      file_path - путь к файлу
    """
    try:
        pattern_date = r"oil_xls_(\d{8})"
        match_date = re.search(pattern_date, file_path)
        if not match_date:
            logging.info(f"Не удалось извлечь дату из имени файла {file_path}")
            return None
        date_doc = match_date.group(1)
        date = datetime.strptime(date_doc, "%Y%m%d").date()

        df = pd.read_excel(file_path, header=None)
        mathed_row = df[df.apply(lambda row: row.astype(str).str.contains("Метрическая тонна").any(), axis=1)].index
        if mathed_row.empty:
            logging.info(f"Ошибка: 'Метрическая тонна' не найдена в файле {file_path}")
            return None
        header_row = mathed_row[0]

        res_df = pd.read_excel(file_path, header=header_row + 2)
        return date, res_df

    except Exception as e:
        logging.exception(f"Ошибка при парсинге файлов в {file_path}: {e}", stack_info=True)


def save_in_db(date: datetime.date, res_df: DataFrame, session):
    """
    Создаем объект SpimexTradingResult и его сохраняем в базу данных
      date - дата файла
      res_df - DataFrame c данными из таблицы(файла)
    """
    try:
        for index in range(100000):
            rows = res_df.iloc[index].to_list()
            if rows[1] in ("Итого:", "Итого: ", " Итого:", "Итого по секции:"):
                break
            if pd.isna(rows[4]) or pd.isna(rows[14]) or pd.isna(rows[5]):
                continue
            if rows[14] == "-":
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
                date=date,
            )
            session.add(new_oil)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Ошибка SQLAlchemy при сохранении объекта в базу данных: {e}")
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при сохранении объекта в базу данных {e}")


def main(year_stop):
    queue = Queue()

    get_urls(URL_WITH_RESULTS, queue, year_stop)
    download_files = []
    for _ in range(queue.qsize()):
        url = queue.get()
        file = download_xml(url, queue)
        download_files.append(file)

    data_to_save = []
    for file_path in download_files:
        data = parse_file(file_path)
        data_to_save.append(data)

    for data in data_to_save:
        if data is None:
            continue
        # Cинхронная сессия для postgresql
        with SessionLocal() as session:
            save_in_db(data[0], data[1], session)


if __name__ == "__main__":
    configure_logging()
    logging.info("Синхронный парсер запущен!")
    arg_parse = configure_argument_parser()
    args = arg_parse.parse_args()
    year_stop = args.year_stop

    logging.info(f"Данные будут загружаться до {year_stop} года.")

    time0 = time()
    logging.info("Начался парсинг..")
    main(year_stop)
    time_ = round((time() - time0), 2)
    logging.info(f"Парсинг завершен время затраченое на работу {time_} секунд.")
