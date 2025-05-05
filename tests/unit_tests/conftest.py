import re

import pytest
import pytest_asyncio
from bs4 import BeautifulSoup


@pytest_asyncio.fixture
async def a_html():
    return """
        <html>
          <body>
            <div>Дата: 11.04.2023</div>
            <a href="/upload/reports/oil_xls/fake.xls">Скачать</a>
            <li class="bx-pag-next"><a href="/next-page">Далее</a></li>
          </body>
        </html>
    """


@pytest_asyncio.fixture
async def a_html_without_next():
    return """
        <html>
          <body>
            <div>Дата: 12.04.2023</div>
            <a href="/upload/reports/oil_xls/fake2.xls">Скачать</a>
          </body>
        </html>
    """


@pytest.fixture
def html():
    return """
        <html>
          <body>
            <div>Дата: 11.04.2023</div>
            <a href="/upload/reports/oil_xls/fake.xls">Скачать</a>
            <li class="bx-pag-next"><a href="/next-page">Далее</a></li>
          </body>
        </html>
    """


@pytest.fixture
def html_without_next():
    return """
        <html>
          <body>
            <div>Дата: 12.04.2023</div>
            <a href="/upload/reports/oil_xls/fake2.xls">Скачать</a>
          </body>
        </html>
    """


@pytest.fixture
def html_page():
    return """
        <html>
          <body>
            <div>11.04.2023</div>
              <a href="/upload/reports/oil_xls/fake.xls">Скачать</a>
            <div>12.04.2023</div>
              <a href="/upload/reports/oil_xls/fake2.xls">Скачать</a>
            <div>12.04.2024</div>
              <a href="/upload/reports/oil_xls/fake3.xls">Скачать</a>
          </body>
        </html>
    """


@pytest_asyncio.fixture
def a_html_page():
    return """
        <html>
          <body>
            <div>11.04.2023</div>
              <a href="/upload/reports/oil_xls/fake.xls">Скачать</a>
            <div>12.04.2023</div>
              <a href="/upload/reports/oil_xls/fake2.xls">Скачать</a>
            <div>12.04.2024</div>
              <a href="/upload/reports/oil_xls/fake3.xls">Скачать</a>
          </body>
        </html>
    """


@pytest.fixture
def create_tags_dates_links(html_page):
    """Даты и ссылки для parse_tags"""
    soup = BeautifulSoup(html_page, "lxml")
    pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    dates = [date.text.strip() for date in soup.find_all(string=pattern_date)]

    links = [a for a in soup.find_all("a", href=True)]

    yield dates, links


@pytest_asyncio.fixture
def a_create_tags_dates_links(a_html_page):
    """Даты и ссылки для parse_tags"""
    soup = BeautifulSoup(a_html_page, "lxml")
    pattern_date = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    dates = [date.text.strip() for date in soup.find_all(string=pattern_date)]

    links = [a for a in soup.find_all("a", href=True)]

    yield dates, links
