from __future__ import annotations

"""Model storing history of generated signals."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class SignalHistory(BaseModel):
    """Represents history of alerts sent to users."""

    __tablename__ = "signal_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pair_id: Mapped[int] = mapped_column(ForeignKey("pairs.id"), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_value: Mapped[float | None] = mapped_column(Float)
    price: Mapped[float | None] = mapped_column(Float)
    volume_change: Mapped[float | None] = mapped_column(Float)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
    processing_time_ms: Mapped[int | None] = mapped_column(Integer)
    delivery_time_ms: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="signal_history")
    pair: Mapped["Pair"] = relationship(back_populates="signal_history")
