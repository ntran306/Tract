import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.models import (
    Profile,
    Property,
    PropertyImage,
    PropertyKind,
    PropertyValuation,
    ValuationSource,
)
from app.schemas.property import (
    ImageAttach,
    PropertyCreate,
    PropertyImageRead,
    PropertyRead,
    PropertyUpdate,
    ValuationCreate,
    ValuationRead,
)
from app.services.analytics import latest_valuations
from app.services.market_data import store_estimate

router = APIRouter()

IMAGE_BUCKET = "property-images"


def _image_url(storage_path: str) -> str:
    base = get_settings().supabase_url.rstrip("/")
    return f"{base}/storage/v1/object/public/{IMAGE_BUCKET}/{storage_path}"


def _images_for(db: Session, property_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[PropertyImage]]:
    if not property_ids:
        return {}
    rows = db.execute(
        select(PropertyImage)
        .where(PropertyImage.property_id.in_(property_ids))
        .order_by(PropertyImage.property_id, PropertyImage.sort_order, PropertyImage.created_at)
    ).scalars()
    out: dict[uuid.UUID, list[PropertyImage]] = {}
    for img in rows:
        out.setdefault(img.property_id, []).append(img)
    return out


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


def _to_read(
    prop: Property,
    valuation: PropertyValuation | None,
    images: list[PropertyImage] | None = None,
) -> PropertyRead:
    out = PropertyRead.model_validate(prop)
    if valuation is not None:
        out.latest_value = valuation.value
        out.latest_value_source = valuation.source
    if images:
        out.images = [PropertyImageRead(id=i.id, url=_image_url(i.storage_path)) for i in images]
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
    ids = [p.id for p in props]
    latest = latest_valuations(db, ids)
    images = _images_for(db, ids)
    return [_to_read(p, latest.get(p.id), images.get(p.id)) for p in props]


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
    images = _images_for(db, [prop.id])
    return _to_read(prop, latest.get(prop.id), images.get(prop.id))


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


@router.post(
    "/{property_id}/hpi-estimate",
    response_model=ValuationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_hpi_estimate(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyValuation:
    # Records an index-based estimate as a valuation. Needs purchase price+date,
    # a state, and HPI data for that state (populated by the refresh_hpi worker).
    val = store_estimate(db, prop)
    if val is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Need purchase price, purchase date, and a state with HPI data to estimate",
        )
    return val


@router.get("/{property_id}/images", response_model=list[PropertyImageRead])
def list_images(
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> list[PropertyImageRead]:
    images = _images_for(db, [prop.id]).get(prop.id, [])
    return [PropertyImageRead(id=i.id, url=_image_url(i.storage_path)) for i in images]


@router.post(
    "/{property_id}/images", response_model=PropertyImageRead, status_code=status.HTTP_201_CREATED
)
def attach_image(
    payload: ImageAttach,
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> PropertyImageRead:
    # The file itself is uploaded client-side straight to Supabase Storage; here
    # we just record its object key against the property. Path must live under
    # this property's folder so one owner can't attach another's uploaded object.
    if not payload.storage_path.startswith(f"{prop.id}/"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "storage_path must be under the property folder")
    count = db.scalar(
        select(func.count()).select_from(PropertyImage).where(PropertyImage.property_id == prop.id)
    )
    img = PropertyImage(property_id=prop.id, storage_path=payload.storage_path, sort_order=count or 0)
    db.add(img)
    db.commit()
    db.refresh(img)
    return PropertyImageRead(id=img.id, url=_image_url(img.storage_path))


@router.delete(
    "/{property_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_image(
    image_id: uuid.UUID,
    prop: Annotated[Property, Depends(get_owned_property)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    img = db.get(PropertyImage, image_id)
    if img is not None and img.property_id == prop.id:
        db.delete(img)  # storage object left in place — prototype; cleanup is a v2 job
        db.commit()
