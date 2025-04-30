import pytest


@pytest.mark.anyio
async def test_status_code(async_client, fastapi_cache_mock):
    days = 4
    response = await async_client.get(f"/results/dates/{days}")
    assert response.status_code == 200
        