import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import UserRole, db_enum


class Profile(Base):
    """App profile, 1:1 with Supabase auth.users (FK added in migration 001;
    the row is inserted by the signup trigger from migration 003)."""

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(
        db_enum(UserRole, "user_role"), default=UserRole.user, server_default="user"
    )
    email_mirror: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    email_digest: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
