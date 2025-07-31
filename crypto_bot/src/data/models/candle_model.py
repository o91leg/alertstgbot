from __future__ import annotations

"""Candle (OHLCV) data model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class Candle(BaseModel):
    """Stores OHLCV data for trading pairs."""

    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_id: Mapped[int] = mapped_column(ForeignKey("pairs.id"), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open_price: Mapped[float] = mapped_column(Float, nullable=False)
    high_price: Mapped[float] = mapped_column(Float, nullable=False)
    low_price: Mapped[float] = mapped_column(Float, nullable=False)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    quote_volume: Mapped[float] = mapped_column(Float, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pair: Mapped["Pair"] = relationship(back_populates="candles")

    __table_args__ = (
        Index("ix_candles_pair_tf_open", "pair_id", "timeframe", "open_time"),
        Index("ix_candles_open_time", "open_time"),
    )
