import pytest
from datetime import date

@pytest.mark.anyio
async def test_404_not_found(async_client):
    days = 10
    response = await async_client.get(f"/results/dates/{days}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_statuc_code_200(async_client, fill_db_spimex_results):
    days = 10
    response = await async_client.get(f"/results/dates/{days}")
    print(response.json())
    assert response.status_code == 200


@pytest.mark.anyio
async def test_format_response(async_client, fill_db_spimex_results):
    days = 3

    response = await async_client.get(f"/results/dates/{days}")
    data = response.json()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    print(data)
    assert isinstance(data, list)