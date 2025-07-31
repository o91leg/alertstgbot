from __future__ import annotations

"""User model definition."""

from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Boolean, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class User(BaseModel):
    """Telegram user representation."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    language_code: Mapped[Optional[str]] = mapped_column(String(10))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_signals_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    real_time_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    real_time_performance_stats: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=dict)

    # relationships
    user_pairs: Mapped[list["UserPair"]] = relationship(back_populates="user")
    signal_history: Mapped[list["SignalHistory"]] = relationship(back_populates="user")

    @property
    def display_name(self) -> str:
        """Return a human friendly display name."""

        return self.username or " ".join(filter(None, [self.first_name, self.last_name]))

    def update_from_telegram(self, telegram_user: Any) -> None:
        """Update fields based on Telegram user object."""

        self.id = telegram_user.id
        self.username = getattr(telegram_user, "username", None)
        self.first_name = getattr(telegram_user, "first_name", None)
        self.last_name = getattr(telegram_user, "last_name", None)
        self.language_code = getattr(telegram_user, "language_code", None)

    def toggle_notifications(self) -> bool:
        """Toggle notifications and return new state."""

        self.notifications_enabled = not self.notifications_enabled
        return self.notifications_enabled

    def increment_signals_count(self) -> None:
        """Increment count of received signals."""

        self.total_signals_received += 1

    def enable_real_time_monitoring(self) -> None:
        """Enable real-time monitoring for user."""

        self.real_time_enabled = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize model to dictionary."""

        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "notifications_enabled": self.notifications_enabled,
            "is_active": self.is_active,
            "is_blocked": self.is_blocked,
            "total_signals_received": self.total_signals_received,
            "real_time_enabled": self.real_time_enabled,
            "real_time_performance_stats": self.real_time_performance_stats,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
