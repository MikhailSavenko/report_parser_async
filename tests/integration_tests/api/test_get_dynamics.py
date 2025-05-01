import pytest
from fastapi import status

@pytest.mark.anyio
async def test_404_not_found(async_client):
    start_date = "2020-10-10"
    end_date = "2020-10-10"
    response = await async_client.get(f"/results/dates/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_200_ok(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")

    response = await async_client.get(f"/results/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_filter_oil_id(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")
    oil_id = fill_db_spimex_results[0].get("oil_id")

    response = await async_client.get(f"/results/{start_date}/{end_date}?oil_id={oil_id}")

    assert len(response.json()) == 2

