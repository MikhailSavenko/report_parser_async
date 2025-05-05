import pytest
from parser import async_parser
from pytest_mock import MockFixture


# @pytest.mark.asyncio
# async def test_main(mocker: MockFixture):

#     mock_get_urls = mocker.patch("parser.async_parser.get_urls", new_callable=mocker.AsyncMock)
#     mock_creaate_task = mocker.patch("parser.async_parser.asyncio.create_task", new_callable=mocker.AsyncMock)

#     await async_parser.main(2023)

#     mock_get_urls.assert_called_once()
#     mock_creaate_task.call_count == 100, "Столько раз не вызывали"