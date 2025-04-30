import pytest


@pytest.mark.anyio
async def test_404_not_found(async_client):
    days = 0
    response = await async_client.get(f"/results/dates/{days}")
    assert response.status_code == 404


