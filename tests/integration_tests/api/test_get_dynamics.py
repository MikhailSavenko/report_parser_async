import pytest
from fastapi import status

@pytest.mark.anyio
async def test_404_not_found(async_client):
    start_date = "2020-10-10"
    end_date = "2020-10-10"
    response = await async_client.get(f"/results/dates/{start_date}/{end_date}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    