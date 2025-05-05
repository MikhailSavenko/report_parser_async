import pytest
from parser import async_parser
from pytest_mock import MockFixture


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