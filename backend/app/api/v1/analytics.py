from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Profile
from app.schemas.analytics import PortfolioSummary
from app.services.analytics import portfolio_summary

router = APIRouter()


@router.get("/portfolio", response_model=PortfolioSummary)
def get_portfolio(
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioSummary:
    return portfolio_summary(db, user)
