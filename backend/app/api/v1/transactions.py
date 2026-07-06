import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models import Profile, Property, Transaction, TxnCategory, TxnKind
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    category_matches_kind,
)

router = APIRouter()


def _owned_property(db: Session, user: Profile, property_id: uuid.UUID) -> Property:
    prop = db.get(Property, property_id)
    if prop is None or prop.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Property not found")
    return prop


def _owned_transaction(db: Session, user: Profile, txn_id: uuid.UUID) -> Transaction:
    txn = db.get(Transaction, txn_id)
    if txn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")
    _owned_property(db, user, txn.property_id)
    return txn


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    property_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    kind: TxnKind | None = None,
    category: TxnCategory | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Transaction]:
    q = (
        select(Transaction)
        .join(Property, Transaction.property_id == Property.id)
        .where(Property.owner_id == user.id)
        .order_by(Transaction.occurred_on.desc(), Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if property_id is not None:
        q = q.where(Transaction.property_id == property_id)
    if date_from is not None:
        q = q.where(Transaction.occurred_on >= date_from)
    if date_to is not None:
        q = q.where(Transaction.occurred_on <= date_to)
    if kind is not None:
        q = q.where(Transaction.kind == kind)
    if category is not None:
        q = q.where(Transaction.category == category)
    return list(db.execute(q).scalars())


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Transaction:
    _owned_property(db, user, payload.property_id)
    txn = Transaction(**payload.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.patch("/{txn_id}", response_model=TransactionRead)
def update_transaction(
    txn_id: uuid.UUID,
    payload: TransactionUpdate,
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Transaction:
    txn = _owned_transaction(db, user, txn_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(txn, field, value)
    if not category_matches_kind(txn.kind, txn.category):
        db.rollback()
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"category '{txn.category.value}' does not match kind '{txn.kind.value}'",
        )
    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    txn_id: uuid.UUID,
    user: Annotated[Profile, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    txn = _owned_transaction(db, user, txn_id)
    db.delete(txn)
    db.commit()
