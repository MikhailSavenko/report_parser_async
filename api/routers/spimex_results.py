from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from api.backend.db_depends import get_db
from db.models import SpimexTradingResult
from api.schemas import SpimexTradingResultDB

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/", response_model=list[SpimexTradingResultDB])
async def get_trading_results(db: Annotated[AsyncSession, Depends(get_db)], 
                              limit: int = Query(10, ge=0, le=10), 
                              offset: int = Query(0, ge=0),
                              oil_id: Annotated[str | None, Query()] = None,
                              delivery_type_id: Annotated[str | None, Query()] = None,
                              delivery_basis_id: Annotated[str | None, Query()] = None):
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no trading results!"
        )
    return results.all()



@router.get("/dates/{days}", response_model=list[date])
async def get_last_trading_dates(db: Annotated[AsyncSession, Depends(get_db)], days: int):
    """Cписок дат последних торговых дней"""
    stmp = select(SpimexTradingResult.date).distinct().order_by(SpimexTradingResult.date.desc()).limit(days)
    dates = await db.scalars(stmp)
    return dates
