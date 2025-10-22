import os
from dotenv import load_dotenv

load_dotenv()

def _get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# Supported timeframes
SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1D", "1w", "1W"]

# Supported LLM models
SUPPORTED_MODELS = {
    "grok-4": "x-ai/grok-4",
    "grok-beta": "x-ai/grok-beta",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "claude-sonnet-3.5": "anthropic/claude-3.5-sonnet",
    "claude-opus-3.5": "anthropic/claude-opus-3.5",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "deepseek-r1": "deepseek/deepseek-r1",
}

# Supported DEXes
SUPPORTED_DEXES = ["hyperliquid", "lighter"]

def _validate_timeframe(interval: str | None) -> str | None:
    """Validate and normalize timeframe."""
    if not interval:
        return interval
    # Normalize to lowercase, handle 1D -> 1d
    normalized = interval.lower().replace('d', 'd').replace('w', 'w')
    if normalized not in [tf.lower() for tf in SUPPORTED_TIMEFRAMES]:
        import logging
        logging.warning(f"Unsupported timeframe: {interval}. Using default.")
        return None
    return interval

def _resolve_model(model_name: str) -> str:
    """Resolve model name to OpenRouter identifier."""
    if model_name in SUPPORTED_MODELS:
        return SUPPORTED_MODELS[model_name]
    # If it's already a full identifier (contains /), use as-is
    if "/" in model_name:
        return model_name
    # Default to treating as full identifier
    return model_name

CONFIG = {
    "taapi_api_key": _get_env("TAAPI_API_KEY", required=True),

    # DEX Selection
    "dex": _get_env("DEX", "hyperliquid").lower(),  # hyperliquid or lighter

    # Hyperliquid configuration
    "hyperliquid_private_key": _get_env("HYPERLIQUID_PRIVATE_KEY"),
    "hyperliquid_base_url": _get_env("HYPERLIQUID_BASE_URL"),
    "hyperliquid_network": _get_env("HYPERLIQUID_NETWORK", "mainnet"),

    # Lighter configuration
    "lighter_private_key": _get_env("LIGHTER_PRIVATE_KEY") or _get_env("HYPERLIQUID_PRIVATE_KEY"),
    "lighter_rpc_url": _get_env("LIGHTER_RPC_URL", "https://rpc.ankr.com/arbitrum"),
    "lighter_chain_id": int(_get_env("LIGHTER_CHAIN_ID", "42161")),  # Arbitrum mainnet
    "lighter_router_address": _get_env("LIGHTER_ROUTER_ADDRESS", "0x..."),  # Update with actual address
    "lighter_use_market_making": _get_env("LIGHTER_USE_MARKET_MAKING", "false").lower() in ("true", "1", "yes"),

    # Common wallet config
    "mnemonic": _get_env("MNEMONIC"),

    # LLM via OpenRouter
    "openrouter_api_key": _get_env("OPENROUTER_API_KEY", required=True),
    "openrouter_base_url": _get_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    "openrouter_referer": _get_env("OPENROUTER_REFERER"),
    "openrouter_app_title": _get_env("OPENROUTER_APP_TITLE", "trading-agent"),
    "llm_model": _resolve_model(_get_env("LLM_MODEL", "grok-4")),

    # Runtime controls via env
    "assets": _get_env("ASSETS"),  # e.g., "BTC ETH SOL" or "BTC,ETH,SOL"
    "interval": _validate_timeframe(_get_env("INTERVAL")),  # e.g., "5m", "15m", "1h", "4h", "1d"

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

    # Market Making Strategy parameters (for Lighter)
    "mm_spread_bps": int(_get_env("MM_SPREAD_BPS", "10")),  # Spread in basis points
    "mm_order_size_usd": float(_get_env("MM_ORDER_SIZE_USD", "100.0")),  # Order size in USD
    "mm_num_levels": int(_get_env("MM_NUM_LEVELS", "3")),  # Number of price levels
    "mm_level_spacing_bps": int(_get_env("MM_LEVEL_SPACING_BPS", "5")),  # Spacing between levels
    "mm_refresh_interval_sec": int(_get_env("MM_REFRESH_INTERVAL_SEC", "30")),  # How often to refresh orders
}
