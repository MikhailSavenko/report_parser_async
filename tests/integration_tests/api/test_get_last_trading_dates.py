import pytest
from datetime import date, datetime
from fastapi import status


@pytest.mark.anyio
async def test_404_not_found(async_client):
    days = 0
    response = await async_client.get(f"/results/dates/{days}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_statuc_code_200(async_client, fill_db_spimex_results):
    days = 10
    response = await async_client.get(f"/results/dates/{days}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_format_response(async_client, fill_db_spimex_results):
    days = 3

    response = await async_client.get(f"/results/dates/{days}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    assert isinstance(data, list)

    date_str = data[0]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    assert isinstance(date_obj, date)


@pytest.mark.anyio
async def test_not_valid_day(async_client, fill_db_spimex_results):
    not_valid_days = "not_valid"
    response = await async_client.get(f"/results/dates/{not_valid_days}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_last_days_result(async_client, fill_db_spimex_results):
    """Проверяем возврат именно посленей записи по дате"""
    days = 1
    last_date = fill_db_spimex_results[-1].get("date")
    response = await async_client.get(f"/results/dates/{days}")

    date_str = response.json()[0]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    assert date_obj == last_date