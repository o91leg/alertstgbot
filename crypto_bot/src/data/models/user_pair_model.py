from __future__ import annotations

"""Association table between users and trading pairs."""

from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class UserPair(BaseModel):
    """Link between User and Pair with settings."""

    __tablename__ = "user_pairs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    pair_id: Mapped[int] = mapped_column(ForeignKey("pairs.id"), primary_key=True)
    timeframes: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=dict)
    signals_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    custom_settings: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=dict)
    real_time_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_signal_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="user_pairs")
    pair: Mapped["Pair"] = relationship(back_populates="user_pairs")
