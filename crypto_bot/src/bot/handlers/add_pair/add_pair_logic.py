from __future__ import annotations

"""Business logic for adding new trading pairs."""

from typing import Any, Dict

import httpx

from src.config.bot_config import BotConfig
from src.data.models import Pair
from src.data.repositories.pair_repository import PairRepository
from src.data.repositories.user_pair_repository import UserPairRepository
from src.utils.validators import normalize_trading_symbol, validate_trading_pair_symbol

config = BotConfig()
pair_repository = PairRepository()
user_pair_repository = UserPairRepository()


async def process_symbol_input(symbol: str) -> Dict[str, Any]:
    """Validate and fetch information about ``symbol`` from Binance API."""

    if not validate_trading_pair_symbol(symbol):
        return {"valid": False, "pair_info": None, "error": "Некорректный символ"}

    normalized = normalize_trading_symbol(symbol)
    url = "https://api.binance.com/api/v3/exchangeInfo"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"symbol": normalized})
    if resp.status_code != 200:
        return {"valid": False, "pair_info": None, "error": "Пара не найдена"}
    data = resp.json().get("symbols", [])
    if not data:
        return {"valid": False, "pair_info": None, "error": "Пара недоступна"}
    info = data[0]
    return {
        "valid": True,
        "pair_info": {
            "symbol": info["symbol"],
            "base_asset": info["baseAsset"],
            "quote_asset": info["quoteAsset"],
        },
        "error": "",
    }


async def execute_add_pair(
    session, user, symbol: str
) -> Pair:  # type: ignore[valid-type]
    """Create pair and user relation with default settings."""

    normalized = normalize_trading_symbol(symbol)
    pair = await pair_repository.get_by_symbol(session, normalized)
    if not pair:
        pair = await pair_repository.create(session, {"symbol": normalized})
    timeframes = {tf: True for tf in config.default_timeframes}
    await user_pair_repository.create(
        session,
        {
            "user_id": user.id,
            "pair_id": pair.id,
            "timeframes": timeframes,
            "real_time_active": config.real_time_enabled,
        },
    )
    return pair
