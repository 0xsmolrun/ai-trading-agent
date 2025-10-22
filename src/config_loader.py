import os
from dotenv import load_dotenv

load_dotenv()

def _get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

CONFIG = {
    "taapi_api_key": _get_env("TAAPI_API_KEY", required=True),
    "hyperliquid_private_key": _get_env("HYPERLIQUID_PRIVATE_KEY") or _get_env("LIGHTER_PRIVATE_KEY"),
    "mnemonic": _get_env("MNEMONIC"),
    # Hyperliquid network/base URL overrides
    "hyperliquid_base_url": _get_env("HYPERLIQUID_BASE_URL"),
    "hyperliquid_network": _get_env("HYPERLIQUID_NETWORK", "mainnet"),
    # LLM via OpenRouter
    "openrouter_api_key": _get_env("OPENROUTER_API_KEY", required=True),
    "openrouter_base_url": _get_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    "openrouter_referer": _get_env("OPENROUTER_REFERER"),
    "openrouter_app_title": _get_env("OPENROUTER_APP_TITLE", "trading-agent"),
    "llm_model": _get_env("LLM_MODEL", "x-ai/grok-4"),
    # Runtime controls via env
    "assets": _get_env("ASSETS"),  # e.g., "BTC ETH SOL" or "BTC,ETH,SOL"
    "interval": _get_env("INTERVAL"),  # e.g., "5m", "1h"
    # API server
    "api_host": _get_env("API_HOST", "0.0.0.0"),
    "api_port": _get_env("APP_PORT") or _get_env("API_PORT") or "3000",
    # Strategy configuration
    "use_strategy": _get_env("USE_STRATEGY", "false").lower() in ("true", "1", "yes"),
    "strategy_name": _get_env("STRATEGY_NAME", "trader_xo"),
    "strategy_mode": _get_env("STRATEGY_MODE", "standalone"),  # standalone or hybrid
    # Trader XO Strategy parameters
    "trader_xo_fast_ema": int(_get_env("TRADER_XO_FAST_EMA", "12")),
    "trader_xo_slow_ema": int(_get_env("TRADER_XO_SLOW_EMA", "25")),
    "trader_xo_ma_filter_period": int(_get_env("TRADER_XO_MA_FILTER_PERIOD", "200")),
    "trader_xo_ma_filter_type": _get_env("TRADER_XO_MA_FILTER_TYPE", "EMA"),  # EMA, SMA, WMA, None
    "trader_xo_stop_loss_percent": float(_get_env("TRADER_XO_STOP_LOSS_PERCENT", "7.0")),
    "trader_xo_use_stop_loss": _get_env("TRADER_XO_USE_STOP_LOSS", "true").lower() in ("true", "1", "yes"),
    "trader_xo_use_stoch_confirmation": _get_env("TRADER_XO_USE_STOCH_CONFIRMATION", "false").lower() in ("true", "1", "yes"),
}
