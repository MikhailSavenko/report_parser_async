from parser import parser
from pytest_mock import MockFixture
from queue import Queue
import pytest
from parser.exceptions import YearComplited
from http import HTTPStatus
from pathlib import Path
from datetime import date
import pandas


from db.models import SpimexTradingResult


def test_main_with_mocks(mocker: MockFixture):
    """Тест main в parser"""
    # Моки
    mock_get_urls = mocker.patch("parser.parser.get_urls")
    mock_download_xml = mocker.patch("parser.parser.download_xml")
    mock_parse_file = mocker.patch("parser.parser.parse_file")
    mock_save_in_db = mocker.patch("parser.parser.save_in_db")

    # Готовим urls
    def fake_get_urls(url, queue, year):
        queue.put("http://example.com/fake.xml")

    mock_get_urls.side_effect = fake_get_urls

    dummy_file_path = "/fake/file.xml"
    dummy_data = ("date", "res_df")

    mock_download_xml.return_value = dummy_file_path
    mock_parse_file.return_value = dummy_data

    # Запуск метода
    parser.main(2023)
    # Утверждаем

    mock_get_urls.assert_called_once()
    mock_download_xml.assert_called_once_with("http://example.com/fake.xml", mocker.ANY)
    mock_parse_file.assert_called_once_with(dummy_file_path)
    mock_save_in_db.assert_called_once()


def test_get_urls(mocker: MockFixture, html, html_without_next):
    mock_request_get = mocker.patch("requests.get")
    mock_parse_tags = mocker.patch("parser.parser.parse_tags")
    mock_get_urls = mocker.patch("parser.parser.get_urls", wraps=parser.get_urls)

    mock_request_get.side_effect = [
        mocker.Mock(text=html),
        mocker.Mock(text=html_without_next)
    ]
    # Вызов тестируемого метода
    queue = Queue()
    parser.get_urls("http://example.com/fake", queue, 2023)

    assert mock_parse_tags.call_count == 2, "Не был вызван parse_tags"
    assert mock_get_urls.call_count == 2, "Не был вызван get_urls"

    first_call_args = mock_parse_tags.call_args_list[0][0]
    second_call_args = mock_parse_tags.call_args_list[1][0]

    assert "11.04.2023" in first_call_args[0][0]
    assert "12.04.2023" in second_call_args[0][0]
 
    assert "/upload/reports/oil_xls/fake.xls" in first_call_args[1][0]["href"]
    assert "/upload/reports/oil_xls/fake2.xls" in second_call_args[1][0]["href"]


def test_parse_tags(mocker: MockFixture, create_tags_dates_links):
    queue = Queue()
    assert queue.empty() == True, "Очередь не пуская до вызова!"
    
    dates, links = create_tags_dates_links

    parser.parse_tags(dates[:2], links[:2], queue, 2024)
    
    assert not queue.empty(), "Очередь пустая после обработки данных. Должно быть два!"
    assert queue.qsize() == 2
    assert queue.queue[0] == links[0].get("href")
    assert queue.queue[1] == links[1].get("href")


def test_parse_tags_year_complited(mocker: MockFixture, create_tags_dates_links):
    """Тест остановки парсинга тегов по году и поднятия YearComplited"""
    queue = Queue()
    assert queue.empty() is True, "Очередь не пуская до вызова!"
    
    dates, links = create_tags_dates_links

    with pytest.raises(YearComplited):
        parser.parse_tags(dates, links, queue, 2024)


def test_download_xml(mocker: MockFixture):
    try:
        dummy_url = "/upload/reports/oil_xls/fake.xls"

        queue = Queue()
        queue.put(dummy_url)

        dummy_content = b"Test Content" 

        mock_response = mocker.Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = dummy_content

        mock_request_get = mocker.patch("requests.get")
        mock_request_get.return_value = mock_response

        url = queue.get()
        file_path = parser.download_xml(url, queue)

        assert file_path is not None, "Путь к файлу некорретен"
        assert file_path.endswith("fake.xls"), "Ожидается иное имя файла"

        full_path = Path(file_path)

        assert full_path.exists(), "Файла нет в downloads!"
        assert full_path.read_bytes() == dummy_content, "Неверный контент в файле!"

        assert queue.empty(), "Очередь не пуста"
    finally:
        if full_path.exists():
            full_path.unlink()


def test_parse_file(mocker: MockFixture):
    dump_file = "oil_xls_20240110162000.xls"

    df_mock = pandas.DataFrame([
        ["что-то", "Метрическая тонна", "еще"], 
        ["ряд", "какой-то", "нужный"]
    ])

    mock_real_excel = mocker.patch("parser.parser.pd.read_excel")
    
    mock_real_excel.side_effect = [df_mock, "RESULT_DF"]

    result = parser.parse_file(dump_file)
    assert result is not None, "Функция должна вернуть кортеж"
    date_result, df_result = result
    
    assert date_result == date(2024, 1, 10)
    assert df_result == "RESULT_DF"
    assert mock_real_excel.call_count == 2
    mock_real_excel.assert_called_with(dump_file, header=2+0)


def test_save_in_db_valid_rows(mocker: MockFixture):
    import datetime
    date = datetime.date(2024, 1, 1)
    data = [
        ["", "1234A56", "Product A", "Basis A", 100, 200, "", "", "", "", "", "", "", "", 3],
        ["", "Итого:", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    ]

    df = pandas.DataFrame(data)

    mock_session = mocker.MagicMock()

    parser.save_in_db(date, df, mock_session)

    assert mock_session.add.call_count == 1, "Не был вызван метод add сессии!"
    
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, SpimexTradingResult), "Объект создан не той модели!"
    assert added_obj.volume == 100
    assert added_obj.total == 200
    assert added_obj.count == 3
    assert added_obj.date == date

    mock_session.commit.assert_called_once(), "Коммит не был вызван!"



