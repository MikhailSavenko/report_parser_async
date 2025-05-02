import pytest
from fastapi import status


@pytest.mark.anyio
async def test_404_not_found(async_client):
    response = await async_client.get("/results/")
    assert response.status_code == status.HTTP_404_NOT_FOUND



@pytest.mark.anyio
async def test_200_ok(async_client, fill_db_spimex_results):
    response = await async_client.get("/results/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_format_response_json(async_client, fill_db_spimex_results):
    response = await async_client.get("/results/")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    assert isinstance(data, list)
    assert isinstance(data[0], dict)

    expected_keys = set(fill_db_spimex_results[0].keys())
    assert expected_keys.issubset(data[0])


@pytest.mark.anyio
async def test_filter_oil_id(async_client, fill_db_spimex_results):
    oil_id = fill_db_spimex_results[0].get("oil_id")

    response = await async_client.get(f"/results/?oil_id={oil_id}")
    data = response.json()
    assert len(data) == 2
    assert data[0].get("oil_id") == oil_id
    assert data[1].get("oil_id") == oil_id

@pytest.mark.anyio
async def test_filter_delivery_type_id(async_client, fill_db_spimex_results):
    delivery_type_id = fill_db_spimex_results[0].get("delivery_type_id")

    response = await async_client.get(f"/results/?delivery_type_id={delivery_type_id}")

    data = response.json()
    assert len(data) == 1
    assert data[0].get("delivery_type_id") == delivery_type_id


@pytest.mark.anyio
async def test_filter_delivery_basis_id(async_client, fill_db_spimex_results):
    delivery_basis_id = fill_db_spimex_results[0].get("delivery_basis_id")

    response = await async_client.get(f"/results/?delivery_basis_id={delivery_basis_id}")

    data = response.json()
    assert len(data) == 2
    assert data[0].get("delivery_basis_id") == delivery_basis_id
    assert data[1].get("delivery_basis_id") == delivery_basis_id


@pytest.mark.anyio
async def test_filter_all(async_client, fill_db_spimex_results):
    delivery_basis_id = fill_db_spimex_results[-1].get("delivery_basis_id")
    delivery_type_id = fill_db_spimex_results[-1].get("delivery_type_id")
    oil_id = fill_db_spimex_results[-1].get("oil_id")

    response = await async_client.get(f"/results/?delivery_basis_id={delivery_basis_id}&delivery_type_id={delivery_type_id}&oil_id={oil_id}")

    data = response.json()
    assert len(data) == 1
    assert data[0].get("delivery_type_id") == delivery_type_id
    assert data[0].get("delivery_basis_id") == delivery_basis_id
    assert data[0].get("oil_id") == oil_id