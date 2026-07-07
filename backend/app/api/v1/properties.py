import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Profile, Property, PropertyKind, PropertyValuation, ValuationSource
from app.schemas.property import (
    PropertyCreate,
    PropertyRead,
    PropertyUpdate,
    ValuationCreate,
    ValuationRead,
)
from app.services.analytics import latest_valuations

router = APIRouter()


def get_owned_property(
    property_id: uuid.UUID,
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Property:
    prop = db.get(Property, property_id)
    if prop is None or prop.owner_id != user.id:
        # 404 (not 403) so property ids don't leak existence to non-owners
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Property not found")
    return prop


def _to_read(prop: Property, valuation: PropertyValuation | None) -> PropertyRead:
    out = PropertyRead.model_validate(prop)
    if valuation is not None:
        out.latest_value = valuation.value
        out.latest_value_source = valuation.source
    return out


@router.get("", response_model=list[PropertyRead])
def list_properties(
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    kind: PropertyKind | None = None,
) -> list[PropertyRead]:
    q = select(Property).where(Property.owner_id == user.id).order_by(Property.created_at.desc())
    if kind is not None:
        q = q.where(Property.kind == kind)
    props = list(db.execute(q).scalars())
    latest = latest_valuations(db, [p.id for p in props])
    return [_to_read(p, latest.get(p.id)) for p in props]


@router.post("", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyRead:
    if payload.kind == PropertyKind.my_home:
        exists = db.execute(
            select(Property.id).where(
                Property.owner_id == user.id, Property.kind == PropertyKind.my_home
            )
        ).first()
        if exists:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "You already have a My Home property — edit it instead",
            )

    data = payload.model_dump()
    prop = Property(owner_id=user.id, **data)
    db.add(prop)
    db.flush()

    baseline: PropertyValuation | None = None
    if payload.purchase_price is not None and payload.purchase_date is not None:
        baseline = PropertyValuation(
            property_id=prop.id,
            source=ValuationSource.purchase_price,
            value=payload.purchase_price,
            valued_at=payload.purchase_date,
            note="Purchase price baseline",
        )
        db.add(baseline)

    db.commit()
    db.refresh(prop)
    return _to_read(prop, baseline)


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyRead:
    latest = latest_valuations(db, [prop.id])
    return _to_read(prop, latest.get(prop.id))


@router.patch("/{property_id}", response_model=PropertyRead)
def update_property(
    payload: PropertyUpdate,
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyRead:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    latest = latest_valuations(db, [prop.id])
    return _to_read(prop, latest.get(prop.id))


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    db.delete(prop)  # valuations/transactions/leases cascade via FK
    db.commit()


@router.get("/{property_id}/valuations", response_model=list[ValuationRead])
def list_valuations(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> list[PropertyValuation]:
    return list(
        db.execute(
            select(PropertyValuation)
            .where(PropertyValuation.property_id == prop.id)
            .order_by(PropertyValuation.valued_at.desc(), PropertyValuation.created_at.desc())
        ).scalars()
    )


@router.post(
    "/{property_id}/valuations",
    response_model=ValuationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_valuation(
    payload: ValuationCreate,
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyValuation:
    # Users record manual valuations only; hpi_estimate/rentcast rows come from
    # services (M2 / premium), keeping estimate provenance trustworthy.
    val = PropertyValuation(
        property_id=prop.id, source=ValuationSource.manual, **payload.model_dump()
    )
    db.add(val)
    db.commit()
    db.refresh(val)
    return val
