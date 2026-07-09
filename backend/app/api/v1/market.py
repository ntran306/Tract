from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import MarketHPI, Profile
from app.schemas.market import FMRRead, HPIPoint, HPISeries, RentBenchmark
from app.services.market_data import fmr_for, latest_hpi

router = APIRouter()


@router.get("/hpi", response_model=HPISeries)
def get_hpi(
    _user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    state: Annotated[str, Query(min_length=2, max_length=2)],
) -> HPISeries:
    state = state.upper()
    latest = latest_hpi(db, state)
    if latest is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No HPI data for that state yet")
    points = list(
        db.execute(
            select(MarketHPI)
            .where(MarketHPI.level == "state", MarketHPI.region_code == state)
            .order_by(MarketHPI.period.asc())
        ).scalars()
    )
    return HPISeries(
        state=state,
        region_name=latest.region_name,
        latest_period=latest.period,
        latest_index=latest.index_value,
        points=[HPIPoint.model_validate(p) for p in points],
    )


@router.get("/fmr", response_model=FMRRead)
def get_fmr(
    _user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    state: Annotated[str, Query(min_length=2, max_length=2)],
    bedrooms: Annotated[int, Query(ge=0, le=4)] = 2,
) -> FMRRead:
    fmr = fmr_for(db, state, bedrooms)
    if fmr is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "No FMR data yet — the HUD refresh worker needs an API token",
        )
    return FMRRead.model_validate(fmr)


@router.get("/rent-benchmark", response_model=RentBenchmark)
def rent_benchmark(
    _user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    state: Annotated[str, Query(min_length=2, max_length=2)],
    bedrooms: Annotated[int, Query(ge=0, le=4)],
    rent: Annotated[float, Query(gt=0)],
) -> RentBenchmark:
    from decimal import Decimal

    fmr = fmr_for(db, state, bedrooms)
    if fmr is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No FMR data for that area yet")
    rent_d = Decimal(str(rent))
    delta = ((rent_d - fmr.rent) / fmr.rent * 100).quantize(Decimal("0.1"))
    return RentBenchmark(
        rent=rent_d,
        fmr=fmr.rent,
        area_name=fmr.area_name,
        bedrooms=bedrooms,
        delta_pct=delta,
    )
