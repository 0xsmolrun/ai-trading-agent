"""
Trader XO Strategy with Support/Resistance
Based on @btc_charlie's Pine Script strategy

Strategy Components:
1. Dual EMA System (Fast 12, Slow 25) for trend detection
2. Stochastic RSI with K/D crossovers for momentum
3. MA Filter (200-period) to trade with the trend
4. Configurable stop loss percentage

Signal Logic:
- Buy: Fast EMA crosses above Slow EMA (with MA filter confirmation)
- Sell: Fast EMA crosses below Slow EMA (with MA filter confirmation)
- StochRSI provides additional momentum confirmation
"""

import logging
from typing import Dict, Optional, List
from collections import deque


class TraderXOStrategy:
    """
    Trader XO Strategy implementation.

    This strategy uses EMA crossovers as primary signals, with optional
    Stochastic RSI confirmation and MA filter for trend alignment.
    """

    def __init__(
        self,
        fast_ema_period: int = 12,
        slow_ema_period: int = 25,
        ma_filter_period: int = 200,
        ma_filter_type: str = "EMA",  # EMA, SMA, WMA, None
        stoch_rsi_k: int = 3,
        stoch_rsi_d: int = 3,
        stoch_rsi_length: int = 14,
        stoch_length: int = 14,
        stoch_upper_band: int = 80,
        stoch_middle_band: int = 50,
        stoch_lower_band: int = 20,
        stop_loss_percent: float = 7.0,
        use_stop_loss: bool = True,
        use_stoch_confirmation: bool = False,
    ):
        """
        Initialize Trader XO Strategy.

        Args:
            fast_ema_period: Period for fast EMA (default: 12)
            slow_ema_period: Period for slow EMA (default: 25)
            ma_filter_period: Period for MA filter (default: 200)
            ma_filter_type: Type of MA filter - EMA, SMA, WMA, or None (default: EMA)
            stoch_rsi_k: Stochastic K smoothing (default: 3)
            stoch_rsi_d: Stochastic D smoothing (default: 3)
            stoch_rsi_length: RSI length for Stochastic RSI (default: 14)
            stoch_length: Stochastic length (default: 14)
            stoch_upper_band: Upper band for overbought (default: 80)
            stoch_middle_band: Middle band (default: 50)
            stoch_lower_band: Lower band for oversold (default: 20)
            stop_loss_percent: Stop loss percentage (default: 7.0)
            use_stop_loss: Enable stop loss (default: True)
            use_stoch_confirmation: Require Stochastic RSI confirmation (default: False)
        """
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period
        self.ma_filter_period = ma_filter_period
        self.ma_filter_type = ma_filter_type
        self.stoch_rsi_k = stoch_rsi_k
        self.stoch_rsi_d = stoch_rsi_d
        self.stoch_rsi_length = stoch_rsi_length
        self.stoch_length = stoch_length
        self.stoch_upper_band = stoch_upper_band
        self.stoch_middle_band = stoch_middle_band
        self.stoch_lower_band = stoch_lower_band
        self.stop_loss_percent = stop_loss_percent
        self.use_stop_loss = use_stop_loss
        self.use_stoch_confirmation = use_stoch_confirmation

        # Track previous states for crossover detection
        self.prev_states: Dict[str, Dict] = {}

        logging.info(
            f"Initialized TraderXO Strategy: "
            f"EMA({fast_ema_period}/{slow_ema_period}), "
            f"MA Filter({ma_filter_type}-{ma_filter_period}), "
            f"StochRSI confirmation: {use_stoch_confirmation}"
        )

    def calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """
        Calculate EMA for given prices and period.

        Args:
            prices: List of prices (newest last)
            period: EMA period

        Returns:
            EMA value or None if insufficient data
        """
        if not prices or len(prices) < period:
            return None

        # EMA calculation
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Start with SMA

        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def calculate_sma(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Simple Moving Average."""
        if not prices or len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def calculate_wma(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Weighted Moving Average."""
        if not prices or len(prices) < period:
            return None

        weights = list(range(1, period + 1))
        weighted_sum = sum(p * w for p, w in zip(prices[-period:], weights))
        return weighted_sum / sum(weights)

    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate RSI for Stochastic RSI.

        Args:
            prices: List of prices
            period: RSI period

        Returns:
            RSI value or None
        """
        if not prices or len(prices) < period + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        if len(gains) < period:
            return None

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_stochastic_rsi(
        self,
        prices: List[float]
    ) -> Optional[Dict[str, float]]:
        """
        Calculate Stochastic RSI with K and D values.

        Args:
            prices: List of prices

        Returns:
            Dict with 'k' and 'd' values, or None
        """
        if not prices or len(prices) < self.stoch_rsi_length + self.stoch_length:
            return None

        # Calculate RSI series
        rsi_values = []
        for i in range(self.stoch_rsi_length, len(prices) + 1):
            rsi = self.calculate_rsi(prices[:i], self.stoch_rsi_length)
            if rsi is not None:
                rsi_values.append(rsi)

        if len(rsi_values) < self.stoch_length:
            return None

        # Calculate Stochastic of RSI
        stoch_values = []
        for i in range(self.stoch_length, len(rsi_values) + 1):
            window = rsi_values[i - self.stoch_length:i]
            highest = max(window)
            lowest = min(window)

            if highest == lowest:
                stoch_values.append(50.0)
            else:
                stoch = 100 * (rsi_values[i - 1] - lowest) / (highest - lowest)
                stoch_values.append(stoch)

        if len(stoch_values) < self.stoch_rsi_k:
            return None

        # K = SMA of Stochastic
        k = sum(stoch_values[-self.stoch_rsi_k:]) / self.stoch_rsi_k

        # D = SMA of K (we need to track K history for this)
        # For simplicity, we'll calculate D from recent stoch values
        if len(stoch_values) < self.stoch_rsi_k + self.stoch_rsi_d:
            d = k  # Not enough data for D, use K
        else:
            k_values = []
            for i in range(self.stoch_rsi_k, len(stoch_values) + 1):
                k_val = sum(stoch_values[i - self.stoch_rsi_k:i]) / self.stoch_rsi_k
                k_values.append(k_val)
            d = sum(k_values[-self.stoch_rsi_d:]) / self.stoch_rsi_d

        return {"k": k, "d": d}

    def check_ma_filter(
        self,
        current_price: float,
        prices: List[float],
        is_buy: bool
    ) -> bool:
        """
        Check if price respects MA filter.

        Args:
            current_price: Current asset price
            prices: Historical prices
            is_buy: True for buy signal, False for sell

        Returns:
            True if filter passes or disabled
        """
        if self.ma_filter_type == "None":
            return True

        ma_value = None
        if self.ma_filter_type == "EMA":
            ma_value = self.calculate_ema(prices, self.ma_filter_period)
        elif self.ma_filter_type == "SMA":
            ma_value = self.calculate_sma(prices, self.ma_filter_period)
        elif self.ma_filter_type == "WMA":
            ma_value = self.calculate_wma(prices, self.ma_filter_period)

        if ma_value is None:
            logging.warning(f"MA filter value is None, allowing trade")
            return True

        # For buys, price should be above MA; for sells, below MA
        if is_buy:
            return current_price > ma_value
        else:
            return current_price < ma_value

    def analyze(
        self,
        asset: str,
        current_price: float,
        prices: List[float],
        taapi_client=None,
        interval: str = "5m"
    ) -> Dict:
        """
        Analyze market data and generate trading signal.

        Args:
            asset: Asset symbol (e.g., "BTC")
            current_price: Current asset price
            prices: Historical prices (oldest to newest)
            taapi_client: Optional TAAPI client for fetching EMA/StochRSI from API
            interval: Timeframe interval

        Returns:
            Dict with signal, rationale, stop_loss, and take_profit
        """
        result = {
            "signal": "hold",
            "rationale": "",
            "stop_loss": None,
            "take_profit": None,
            "fast_ema": None,
            "slow_ema": None,
            "ma_filter": None,
            "stoch_rsi": None
        }

        if not prices or len(prices) < max(self.fast_ema_period, self.slow_ema_period):
            result["rationale"] = f"Insufficient price data (need {max(self.fast_ema_period, self.slow_ema_period)} bars)"
            return result

        # Calculate EMAs
        if taapi_client:
            try:
                # Fetch from TAAPI for accuracy
                fast_ema_data = taapi_client.fetch_series(
                    "ema",
                    f"{asset}/USDT",
                    interval,
                    results=2,
                    params={"period": self.fast_ema_period}
                )
                slow_ema_data = taapi_client.fetch_series(
                    "ema",
                    f"{asset}/USDT",
                    interval,
                    results=2,
                    params={"period": self.slow_ema_period}
                )

                if fast_ema_data and len(fast_ema_data) >= 2:
                    fast_ema_current = fast_ema_data[0]
                    fast_ema_prev = fast_ema_data[1]
                else:
                    fast_ema_current = self.calculate_ema(prices, self.fast_ema_period)
                    fast_ema_prev = self.calculate_ema(prices[:-1], self.fast_ema_period)

                if slow_ema_data and len(slow_ema_data) >= 2:
                    slow_ema_current = slow_ema_data[0]
                    slow_ema_prev = slow_ema_data[1]
                else:
                    slow_ema_current = self.calculate_ema(prices, self.slow_ema_period)
                    slow_ema_prev = self.calculate_ema(prices[:-1], self.slow_ema_period)
            except Exception as e:
                logging.warning(f"TAAPI EMA fetch failed: {e}, using local calculation")
                fast_ema_current = self.calculate_ema(prices, self.fast_ema_period)
                fast_ema_prev = self.calculate_ema(prices[:-1], self.fast_ema_period)
                slow_ema_current = self.calculate_ema(prices, self.slow_ema_period)
                slow_ema_prev = self.calculate_ema(prices[:-1], self.slow_ema_period)
        else:
            fast_ema_current = self.calculate_ema(prices, self.fast_ema_period)
            fast_ema_prev = self.calculate_ema(prices[:-1], self.fast_ema_period)
            slow_ema_current = self.calculate_ema(prices, self.slow_ema_period)
            slow_ema_prev = self.calculate_ema(prices[:-1], self.slow_ema_period)

        if None in [fast_ema_current, fast_ema_prev, slow_ema_current, slow_ema_prev]:
            result["rationale"] = "Unable to calculate EMAs"
            return result

        result["fast_ema"] = fast_ema_current
        result["slow_ema"] = slow_ema_current

        # Detect EMA crossovers
        bullish_cross = fast_ema_prev <= slow_ema_prev and fast_ema_current > slow_ema_current
        bearish_cross = fast_ema_prev >= slow_ema_prev and fast_ema_current < slow_ema_current

        # Track state to prevent repeated signals
        prev_state = self.prev_states.get(asset, {})
        prev_buy_count = prev_state.get("buy_count", 0)
        prev_sell_count = prev_state.get("sell_count", 0)

        buy_count = prev_buy_count
        sell_count = prev_sell_count

        # Update counts based on EMA relationship
        if fast_ema_current > slow_ema_current:
            buy_count += 1
            sell_count = 0
        elif fast_ema_current < slow_ema_current:
            sell_count += 1
            buy_count = 0

        # Generate signals (only on fresh crossover)
        buysignal = buy_count < 2 and buy_count > 0 and sell_count < 1 and bullish_cross
        sellsignal = sell_count > 0 and sell_count < 2 and buy_count < 1 and bearish_cross

        # Check Stochastic RSI if enabled
        stoch_confirmation = True
        if self.use_stoch_confirmation:
            stoch_rsi = self.calculate_stochastic_rsi(prices)
            if stoch_rsi:
                result["stoch_rsi"] = stoch_rsi
                k, d = stoch_rsi["k"], stoch_rsi["d"]

                # For buy: K crosses above D in oversold/middle zone
                # For sell: K crosses below D in overbought/middle zone
                prev_stoch = prev_state.get("stoch_rsi", {"k": k, "d": d})
                prev_k, prev_d = prev_stoch["k"], prev_stoch["d"]

                k_cross_up = prev_k <= prev_d and k > d and (k < self.stoch_middle_band or d < self.stoch_middle_band)
                k_cross_down = prev_k >= prev_d and k < d and (k > self.stoch_middle_band or d > self.stoch_middle_band)

                if buysignal and not k_cross_up:
                    stoch_confirmation = False
                if sellsignal and not k_cross_down:
                    stoch_confirmation = False

        # Check MA filter
        if buysignal:
            ma_filter_pass = self.check_ma_filter(current_price, prices, is_buy=True)
            if ma_filter_pass and stoch_confirmation:
                result["signal"] = "buy"
                result["rationale"] = (
                    f"BUY: Fast EMA({self.fast_ema_period})={fast_ema_current:.2f} "
                    f"crossed above Slow EMA({self.slow_ema_period})={slow_ema_current:.2f}. "
                )

                if self.ma_filter_type != "None":
                    result["rationale"] += f"Price above {self.ma_filter_type}({self.ma_filter_period}). "

                if self.use_stoch_confirmation and result["stoch_rsi"]:
                    result["rationale"] += f"StochRSI K/D crossover confirmed. "

                if self.use_stop_loss:
                    result["stop_loss"] = current_price * (1 - self.stop_loss_percent / 100)

                # Simple TP based on risk:reward ratio of 2:1
                risk = current_price - result["stop_loss"] if result["stop_loss"] else current_price * 0.07
                result["take_profit"] = current_price + (risk * 2)
            else:
                reasons = []
                if not ma_filter_pass:
                    reasons.append(f"price below {self.ma_filter_type}({self.ma_filter_period})")
                if not stoch_confirmation:
                    reasons.append("StochRSI not confirmed")
                result["rationale"] = f"BUY signal filtered out: {', '.join(reasons)}"

        elif sellsignal:
            ma_filter_pass = self.check_ma_filter(current_price, prices, is_buy=False)
            if ma_filter_pass and stoch_confirmation:
                result["signal"] = "sell"
                result["rationale"] = (
                    f"SELL: Fast EMA({self.fast_ema_period})={fast_ema_current:.2f} "
                    f"crossed below Slow EMA({self.slow_ema_period})={slow_ema_current:.2f}. "
                )

                if self.ma_filter_type != "None":
                    result["rationale"] += f"Price below {self.ma_filter_type}({self.ma_filter_period}). "

                if self.use_stoch_confirmation and result["stoch_rsi"]:
                    result["rationale"] += f"StochRSI K/D crossover confirmed. "

                if self.use_stop_loss:
                    result["stop_loss"] = current_price * (1 + self.stop_loss_percent / 100)

                # Simple TP based on risk:reward ratio of 2:1
                risk = result["stop_loss"] - current_price if result["stop_loss"] else current_price * 0.07
                result["take_profit"] = current_price - (risk * 2)
            else:
                reasons = []
                if not ma_filter_pass:
                    reasons.append(f"price above {self.ma_filter_type}({self.ma_filter_period})")
                if not stoch_confirmation:
                    reasons.append("StochRSI not confirmed")
                result["rationale"] = f"SELL signal filtered out: {', '.join(reasons)}"
        else:
            # No crossover
            if fast_ema_current > slow_ema_current:
                result["rationale"] = f"HOLD: Bullish trend (Fast EMA > Slow EMA), waiting for signal"
            elif fast_ema_current < slow_ema_current:
                result["rationale"] = f"HOLD: Bearish trend (Fast EMA < Slow EMA), waiting for signal"
            else:
                result["rationale"] = f"HOLD: EMAs aligned, no clear trend"

        # Update state for next iteration
        self.prev_states[asset] = {
            "buy_count": buy_count,
            "sell_count": sell_count,
            "fast_ema": fast_ema_current,
            "slow_ema": slow_ema_current,
            "stoch_rsi": result.get("stoch_rsi", prev_state.get("stoch_rsi"))
        }

        return result
