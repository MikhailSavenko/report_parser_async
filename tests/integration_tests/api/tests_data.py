from datetime import datetime, date

spimex_test_data = [
    {
        "exchange_product_id": "EX123",
        "exchange_product_name": "Дизель Летний",
        "oil_id": "OIL01",
        "delivery_basis_id": "DB001",
        "delivery_type_id": "DT001",
        "delivery_basis_name": "Москва",
        "volume": 1000,
        "total": 750000,
        "count": 5,
        "date": date(2024, 5, 20),
        "created_on": datetime(2024, 5, 21, 10, 0, 0),
        "updated_on": None
    },
    {
        "exchange_product_id": "EX124",
        "exchange_product_name": "Бензин АИ-92",
        "oil_id": "OIL01",
        "delivery_basis_id": "DB001",
        "delivery_type_id": "DT002",
        "delivery_basis_name": "Санкт-Петербург",
        "volume": 2000,
        "total": 1400000,
        "count": 10,
        "date": date(2024, 5, 21),
        "created_on": datetime(2024, 5, 22, 11, 30, 0),
        "updated_on": None
    },
    {
        "exchange_product_id": "EX125",
        "exchange_product_name": "Мазут М100",
        "oil_id": "OIL03",
        "delivery_basis_id": "DB003",
        "delivery_type_id": "DT002",
        "delivery_basis_name": "Нижний Новгород",
        "volume": 500,
        "total": 300000,
        "count": 3,
        "date": date(2024, 5, 22),
        "created_on": datetime(2024, 5, 23, 9, 0, 0),
        "updated_on": None
    }
]
