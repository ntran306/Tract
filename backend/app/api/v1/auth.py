from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models import Profile
from app.schemas.profile import ProfileRead

router = APIRouter()


@router.get("/me", response_model=ProfileRead)
def read_me(user: Annotated[Profile, Depends(get_current_user)]) -> Profile:
    return user
