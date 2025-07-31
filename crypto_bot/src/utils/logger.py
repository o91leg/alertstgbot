from __future__ import annotations

"""Logging utilities for the crypto bot."""

from typing import Any

import structlog


class LoggerMixin:
    """Mixin providing a :attr:`logger` attribute using ``structlog``.

    Classes that inherit from this mixin will have a ``logger`` attribute
    initialized with the class name.  Subclasses should call ``super().__init__``
    if they override ``__init__``.
    """

    logger: structlog.stdlib.BoundLogger

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - short
        super().__init__()
        self.logger = structlog.get_logger(self.__class__.__name__)
