from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.properties import get_owned_property
from app.core.deps import get_db
from app.models import Lease, Property, PropertyKind
from app.schemas.property import LeaseRead, LeaseUpsert

router = APIRouter()


def _active_lease(db: Session, prop: Property) -> Lease | None:
    return db.execute(
        select(Lease).where(Lease.property_id == prop.id, Lease.is_active)
    ).scalar_one_or_none()


@router.get("/{property_id}/lease", response_model=LeaseRead)
def get_lease(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> Lease:
    lease = _active_lease(db, prop)
    if lease is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No active lease")
    return lease


@router.put("/{property_id}/lease", response_model=LeaseRead)
def upsert_lease(
    payload: LeaseUpsert,
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> Lease:
    if prop.kind != PropertyKind.rental:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Leases only apply to rental properties"
        )
    lease = _active_lease(db, prop)
    if lease is None:
        lease = Lease(property_id=prop.id, **payload.model_dump())
        db.add(lease)
    else:
        for field, value in payload.model_dump().items():
            setattr(lease, field, value)
    db.commit()
    db.refresh(lease)
    return lease


@router.delete("/{property_id}/lease", status_code=status.HTTP_204_NO_CONTENT)
def delete_lease(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    lease = _active_lease(db, prop)
    if lease is not None:
        db.delete(lease)
        db.commit()
