from datetime import date, datetime

from pydantic import BaseModel


class SpimexTradingResultDB(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_type_id: str
    delivery_basis_name: str
    volume: int
    total: int
    count: int
    date: date
    created_on: datetime
    updated_on: datetime | None = None
