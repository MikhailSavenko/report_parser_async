from datetime import datetime, timezone
from datetime import date as date_doc
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SpimexTradingResult(Base):
    """Класс данных Бюллетени в БД"""
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str] = mapped_column()
    exchange_product_name: Mapped[str] = mapped_column()
    oil_id: Mapped[str] = mapped_column()
    delivery_basis_id: Mapped[str] = mapped_column()
    delivery_type_id: Mapped[str] = mapped_column()
    delivery_basis_name: Mapped[str] = mapped_column()
    volume: Mapped[int] = mapped_column()
    total: Mapped[int] = mapped_column()
    count: Mapped[int] = mapped_column()
    date: Mapped[date_doc] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_on: Mapped[datetime] = mapped_column(default=None, nullable=True)