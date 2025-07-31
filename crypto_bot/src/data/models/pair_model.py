from __future__ import annotations

"""Trading pair model."""

from typing import Any, Dict, Optional
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class Pair(BaseModel):
    """Represents a trading pair (e.g., BTCUSDT)."""

    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    base_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    quote_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_tracked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    users_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    signals_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_price: Mapped[Optional[float]] = mapped_column(Float)
    last_update_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    real_time_monitoring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    performance_metrics: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=dict)

    user_pairs: Mapped[list["UserPair"]] = relationship(back_populates="pair")
    signal_history: Mapped[list["SignalHistory"]] = relationship(back_populates="pair")
    candles: Mapped[list["Candle"]] = relationship(back_populates="pair")

    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading pair symbol."""

        return symbol.isupper() and len(symbol) >= 6

    def update_statistics(self, users_delta: int = 0, signals_delta: int = 0) -> None:
        """Update counts for users and signals."""

        self.users_count += users_delta
        self.signals_count += signals_delta

    def activate_monitoring(self) -> None:
        self.real_time_monitoring = True

    def deactivate_monitoring(self) -> None:
        self.real_time_monitoring = False
