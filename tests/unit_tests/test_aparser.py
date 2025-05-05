import pytest
from parser import async_parser
from pytest_mock import MockFixture
import asyncio

@pytest.mark.asyncio
async def test_main(mocker: MockFixture):
    async def get_fake_urls(url, session, queue, year):
        for i in range(3):
            await queue.put(f"https://example.com/file_{i}.xml")

    async def download_xml_task_down_and_file(url, session_aiohttp, queue):
        queue.task_done()
        return f"file_{url.split('_')[1]}"

    mocker.patch("parser.async_parser.get_urls", 
                 new_callable=mocker.AsyncMock, 
                 side_effect=get_fake_urls)
    
    mocker.patch("parser.async_parser.download_xml", 
                 new_callable=mocker.AsyncMock, 
                 side_effect=download_xml_task_down_and_file)
    
    mock_cover_over_parse_file = mocker.patch("parser.async_parser.cover_over_parse_file",
                                              new_callable=mocker.AsyncMock,
                                              return_value="data_processed")
    mock_save_data_to_db = mocker.patch("parser.async_parser.save_data_to_db",
                                        new_callable=mocker.AsyncMock)
    await async_parser.main(2023)
 
    assert mock_cover_over_parse_file.call_count == 3
    assert mock_save_data_to_db.call_count == 3


@pytest.mark.asyncio
async def test_get_urls(mocker: MockFixture, a_html, a_html_without_next):

    res1 = mocker.AsyncMock()
    res1.text = mocker.AsyncMock(return_value=a_html)

    res2 = mocker.AsyncMock()
    res2.text = mocker.AsyncMock(return_value=a_html_without_next)

    mock_session = mocker.AsyncMock()
    mock_session.get.side_effect = [res1, res2]

    mock_parse_tags = mocker.patch("parser.async_parser.parse_tags",
                                   new_callable=mocker.AsyncMock)
    mock_get_urls = mocker.patch("parser.async_parser.get_urls", wraps=async_parser.get_urls)
    queue = asyncio.Queue()

    await async_parser.get_urls("http://example.com/fake", mock_session, queue, 2023)

    assert mock_parse_tags.call_count == 2, "Не был вызван parse_tags"
    assert mock_get_urls.call_count == 2, "Не был вызван get_urls"

    first_call_args = mock_parse_tags.call_args_list[0][0]
    second_call_args = mock_parse_tags.call_args_list[1][0]

    assert "11.04.2023" in first_call_args[0][0]
    assert "12.04.2023" in second_call_args[0][0]

    assert "/upload/reports/oil_xls/fake.xls" in first_call_args[1][0]["href"]
    assert "/upload/reports/oil_xls/fake2.xls" in second_call_args[1][0]["href"]
    


