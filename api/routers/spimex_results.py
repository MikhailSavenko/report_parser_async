from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.backend.db_depends import get_db
from api.schemas import SpimexTradingResultDB
from api.utils import request_key_builder
from db.models import SpimexTradingResult

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/dates/{days}", response_model=list[date])
@cache(key_builder=request_key_builder)
async def get_last_trading_dates(db: Annotated[AsyncSession, Depends(get_db)], days: int):
    """Cписок дат последних торговых дней"""
    stmp = select(SpimexTradingResult.date).distinct().order_by(SpimexTradingResult.date.desc()).limit(days)

    dates = await db.scalars(stmp)

    if dates is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no trading dates!")
    return dates


@router.get("/{start_date}/{end_date}", response_model=list[SpimexTradingResultDB])
@cache(key_builder=request_key_builder)
async def get_dynamics(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date = Path(example="2025-02-26"),
    end_date: date = Path(example="2025-02-27"),
    limit: int = Query(10, ge=0, le=10),
    offset: int = Query(0, ge=0),
    oil_id: Annotated[str | None, Query()] = None,
    delivery_type_id: Annotated[str | None, Query()] = None,
    delivery_basis_id: Annotated[str | None, Query()] = None,
):
    """Cписок торгов за заданный период"""
    stmp = select(SpimexTradingResult).where(
        SpimexTradingResult.date >= start_date, SpimexTradingResult.date <= end_date
    )

    if oil_id:
        stmp = stmp.where(SpimexTradingResult.oil_id == oil_id)

    if delivery_type_id:
        stmp = stmp.where(SpimexTradingResult.delivery_type_id == delivery_type_id)

    if delivery_basis_id:
        stmp = stmp.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    stmp = stmp.limit(limit).offset(offset)

    results = await db.scalars(stmp)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no trading results!")
    return results.all()


@router.get("/", response_model=list[SpimexTradingResultDB])
@cache(key_builder=request_key_builder)
async def get_trading_results(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=0, le=10),
    offset: int = Query(0, ge=0),
    oil_id: Annotated[str | None, Query()] = None,
    delivery_type_id: Annotated[str | None, Query()] = None,
    delivery_basis_id: Annotated[str | None, Query()] = None,
):
    """Cписок торгов"""
    stmp = select(SpimexTradingResult)

    if oil_id:
        stmp = stmp.where(SpimexTradingResult.oil_id == oil_id)

    if delivery_type_id:
        stmp = stmp.where(SpimexTradingResult.delivery_type_id == delivery_type_id)

    if delivery_basis_id:
        stmp = stmp.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    stmp = stmp.limit(limit).offset(offset)

    results = await db.scalars(stmp)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no trading results!")
    return results.all()
