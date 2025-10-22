"""
Strategy integration helper for Trader XO Strategy.

This module provides a bridge between the Trader XO strategy and the
existing LLM-based trading agent, allowing the strategy to work alongside
or replace the LLM decision maker.
"""

import logging
from typing import Dict, List, Optional
from src.strategies.trader_xo import TraderXOStrategy


class StrategyIntegration:
    """
    Integration layer for trading strategies.

    Provides a unified interface for strategy-based trading decisions
    that can work with the existing trading agent infrastructure.
    """

    def __init__(
        self,
        strategy_name: str = "trader_xo",
        strategy_config: Optional[Dict] = None
    ):
        """
        Initialize strategy integration.

        Args:
            strategy_name: Name of strategy to use (currently only "trader_xo")
            strategy_config: Configuration dict for the strategy
        """
        self.strategy_name = strategy_name
        self.strategy = None

        if strategy_name == "trader_xo":
            config = strategy_config or {}
            self.strategy = TraderXOStrategy(
                fast_ema_period=config.get("fast_ema_period", 12),
                slow_ema_period=config.get("slow_ema_period", 25),
                ma_filter_period=config.get("ma_filter_period", 200),
                ma_filter_type=config.get("ma_filter_type", "EMA"),
                stoch_rsi_k=config.get("stoch_rsi_k", 3),
                stoch_rsi_d=config.get("stoch_rsi_d", 3),
                stoch_rsi_length=config.get("stoch_rsi_length", 14),
                stoch_length=config.get("stoch_length", 14),
                stoch_upper_band=config.get("stoch_upper_band", 80),
                stoch_middle_band=config.get("stoch_middle_band", 50),
                stoch_lower_band=config.get("stoch_lower_band", 20),
                stop_loss_percent=config.get("stop_loss_percent", 7.0),
                use_stop_loss=config.get("use_stop_loss", True),
                use_stoch_confirmation=config.get("use_stoch_confirmation", False),
            )
            logging.info(f"Initialized {strategy_name} strategy with config: {config}")
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    def generate_trade_decisions(
        self,
        assets: List[str],
        market_data: Dict[str, Dict],
        taapi_client=None,
        interval: str = "5m"
    ) -> List[Dict]:
        """
        Generate trade decisions for multiple assets.

        Args:
            assets: List of asset symbols (e.g., ["BTC", "ETH"])
            market_data: Dict mapping asset -> market data
                Expected keys per asset:
                - current_price: Current price
                - price_history: List of historical prices (oldest to newest)
            taapi_client: Optional TAAPI client for indicator fetching
            interval: Trading interval (e.g., "5m", "1h")

        Returns:
            List of trade decision dicts compatible with existing agent format:
            [
                {
                    "asset": "BTC",
                    "action": "buy|sell|hold",
                    "allocation_usd": 0.0,  # Set by caller based on allocation strategy
                    "tp_price": 50000.0,
                    "sl_price": 45000.0,
                    "exit_plan": "...",
                    "rationale": "..."
                }
            ]
        """
        decisions = []

        for asset in assets:
            data = market_data.get(asset, {})
            current_price = data.get("current_price")
            price_history = data.get("price_history", [])

            if not current_price or not price_history:
                logging.warning(f"Insufficient data for {asset}, skipping")
                decisions.append({
                    "asset": asset,
                    "action": "hold",
                    "allocation_usd": 0.0,
                    "tp_price": None,
                    "sl_price": None,
                    "exit_plan": "",
                    "rationale": f"Insufficient market data for {asset}"
                })
                continue

            # Analyze with strategy
            analysis = self.strategy.analyze(
                asset=asset,
                current_price=current_price,
                prices=price_history,
                taapi_client=taapi_client,
                interval=interval
            )

            # Convert to trade decision format
            signal = analysis.get("signal", "hold")
            action = signal  # "buy", "sell", or "hold"

            # Build exit plan
            exit_plan_parts = []
            if analysis.get("stop_loss"):
                exit_plan_parts.append(f"SL at {analysis['stop_loss']:.2f}")
            if analysis.get("take_profit"):
                exit_plan_parts.append(f"TP at {analysis['take_profit']:.2f}")

            # Add strategy-specific exit conditions
            if action == "buy":
                exit_plan_parts.append(
                    f"Exit if Fast EMA({self.strategy.fast_ema_period}) "
                    f"crosses below Slow EMA({self.strategy.slow_ema_period})"
                )
            elif action == "sell":
                exit_plan_parts.append(
                    f"Exit if Fast EMA({self.strategy.fast_ema_period}) "
                    f"crosses above Slow EMA({self.strategy.slow_ema_period})"
                )

            exit_plan = "; ".join(exit_plan_parts) if exit_plan_parts else "Hold until signal reversal"

            decision = {
                "asset": asset,
                "action": action,
                "allocation_usd": 0.0,  # Will be set by allocation logic
                "tp_price": analysis.get("take_profit"),
                "sl_price": analysis.get("stop_loss"),
                "exit_plan": exit_plan,
                "rationale": analysis.get("rationale", ""),
                # Additional metadata
                "strategy": self.strategy_name,
                "fast_ema": analysis.get("fast_ema"),
                "slow_ema": analysis.get("slow_ema"),
                "stoch_rsi": analysis.get("stoch_rsi"),
            }

            decisions.append(decision)
            logging.info(
                f"{asset}: {action.upper()} - {analysis.get('rationale', '')}"
            )

        return decisions

    def format_strategy_context(
        self,
        asset: str,
        market_data: Dict
    ) -> str:
        """
        Format market data for inclusion in LLM context (if using hybrid approach).

        Args:
            asset: Asset symbol
            market_data: Market data dict for the asset

        Returns:
            Formatted string with strategy indicators
        """
        if not self.strategy or not hasattr(self.strategy, 'prev_states'):
            return ""

        state = self.strategy.prev_states.get(asset, {})
        fast_ema = state.get("fast_ema")
        slow_ema = state.get("slow_ema")
        stoch_rsi = state.get("stoch_rsi")

        lines = [f"\n=== Trader XO Strategy Indicators for {asset} ==="]

        if fast_ema and slow_ema:
            lines.append(f"Fast EMA({self.strategy.fast_ema_period}): {fast_ema:.2f}")
            lines.append(f"Slow EMA({self.strategy.slow_ema_period}): {slow_ema:.2f}")
            trend = "Bullish" if fast_ema > slow_ema else "Bearish"
            lines.append(f"EMA Trend: {trend}")

        if stoch_rsi:
            lines.append(f"Stochastic RSI K: {stoch_rsi['k']:.2f}")
            lines.append(f"Stochastic RSI D: {stoch_rsi['d']:.2f}")

            if stoch_rsi['k'] > self.strategy.stoch_upper_band:
                momentum = "Overbought"
            elif stoch_rsi['k'] < self.strategy.stoch_lower_band:
                momentum = "Oversold"
            else:
                momentum = "Neutral"
            lines.append(f"Momentum: {momentum}")

        return "\n".join(lines)
