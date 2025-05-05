import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_404_not_found(async_client):
    start_date = "2020-10-10"
    end_date = "2020-10-10"
    response = await async_client.get(f"/results/dates/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_200_ok(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")

    response = await async_client.get(f"/results/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_filter_oil_id(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")
    oil_id = fill_db_spimex_results[0].get("oil_id")

    response = await async_client.get(f"/results/{start_date}/{end_date}?oil_id={oil_id}")
    data = response.json()
    assert len(data) == 2
    assert data[0].get("oil_id") == oil_id
    assert data[1].get("oil_id") == oil_id



@pytest.mark.asyncio
async def test_filter_delivery_type_id(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")
    delivery_type_id = fill_db_spimex_results[0].get("delivery_type_id")

    response = await async_client.get(f"/results/{start_date}/{end_date}?delivery_type_id={delivery_type_id}")
    data = response.json()
    assert len(data) == 1
    assert data[0].get("delivery_type_id") == delivery_type_id


@pytest.mark.asyncio
async def test_filter_delivery_basis_id(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")
    delivery_basis_id = fill_db_spimex_results[0].get("delivery_basis_id")

    response = await async_client.get(f"/results/{start_date}/{end_date}?delivery_basis_id={delivery_basis_id}")
    data = response.json()
    assert len(data) == 2
    assert data[0].get("delivery_basis_id") == delivery_basis_id
    assert data[1].get("delivery_basis_id") == delivery_basis_id


@pytest.mark.asyncio
async def test_filter_all(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")
    delivery_basis_id = fill_db_spimex_results[-1].get("delivery_basis_id")
    delivery_type_id = fill_db_spimex_results[-1].get("delivery_type_id")
    oil_id = fill_db_spimex_results[-1].get("oil_id")

    response = await async_client.get(f"/results/{start_date}/{end_date}?delivery_basis_id={delivery_basis_id}&delivery_type_id={delivery_type_id}&oil_id={oil_id}")
    data = response.json()
    assert len(data) == 1
    assert data[0].get("delivery_type_id") == delivery_type_id
    assert data[0].get("delivery_basis_id") == delivery_basis_id
    assert data[0].get("oil_id") == oil_id


@pytest.mark.asyncio
async def test_format_response_json(async_client, fill_db_spimex_results):
    start_date = fill_db_spimex_results[0].get("date")
    end_date = fill_db_spimex_results[-1].get("date")

    response = await async_client.get(f"/results/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    assert isinstance(data, list)
    assert isinstance(data[0], dict)

    expected_keys = set(fill_db_spimex_results[0].keys())
    assert expected_keys.issubset(data[0])


@pytest.mark.asyncio
@pytest.mark.parametrize("start_date, end_date", [
    ("22-01-2024", "22-01-2024"),
    ("2024.01.22", "2024.01.22"),
    ("aaa", "aaa"),
    (11111111111, 111111111111)

])
async def test_not_valid_dates(start_date, end_date, async_client, fill_db_spimex_results):
    response = await async_client.get(f"/results/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY