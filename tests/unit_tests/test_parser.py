from parser import parser
from pytest_mock import MockFixture
from queue import Queue


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


def test_get_urls(mocker: MockFixture):
    mock_request_get = mocker.patch("requests.get")
    mock_parse_tags = mocker.patch("parser.parser.parse_tags")

    html = """
        <html>
          <body>
            <div>Дата: 11.04.2023</div>
            <a href="/upload/reports/oil_xls/fake.xls">Скачать</a>
          </body>
        </html>
    """
    mock_request_get.return_value.text = html
    # Вызов
    queue = Queue()
    parser.get_urls("http://example.com/fake", queue, 2023)

    mock_parse_tags.assert_called_once()