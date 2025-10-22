"""
Market Making Strategy

A simple but effective market making strategy that places buy and sell
orders around the mid price to capture the spread.

Strategy Logic:
1. Monitor mid price for each asset
2. Place tiered buy/sell orders around mid price
3. Refresh orders periodically
4. Can be combined with Trader XO for directional bias
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone


class MarketMakingStrategy:
    """
    Market making strategy for DEX order books.

    Places symmetric buy/sell orders around mid price to capture spread.
    Optionally applies directional bias from Trader XO signals.
    """

    def __init__(
        self,
        spread_bps: int = 10,
        order_size_usd: float = 100.0,
        num_levels: int = 3,
        level_spacing_bps: int = 5,
        refresh_interval_sec: int = 30,
        skew_on_signal: bool = True,
        skew_amount: float = 0.3
    ):
        """
        Initialize market making strategy.

        Args:
            spread_bps: Half-spread in basis points (10 = 0.1%)
            order_size_usd: Order size in USD per level
            num_levels: Number of price levels on each side
            level_spacing_bps: Spacing between levels in bps
            refresh_interval_sec: How often to refresh orders
            skew_on_signal: Apply directional skew based on signals
            skew_amount: How much to skew sizes (0.3 = 30% more on signal side)
        """
        self.spread_bps = spread_bps
        self.order_size_usd = order_size_usd
        self.num_levels = num_levels
        self.level_spacing_bps = level_spacing_bps
        self.refresh_interval_sec = refresh_interval_sec
        self.skew_on_signal = skew_on_signal
        self.skew_amount = skew_amount

        # Track last refresh time per asset
        self.last_refresh: Dict[str, datetime] = {}

        logging.info(
            f"Market Making Strategy initialized: "
            f"spread={spread_bps}bps, levels={num_levels}, size=${order_size_usd}"
        )

    def should_refresh(self, asset: str) -> bool:
        """
        Check if orders should be refreshed for asset.

        Args:
            asset: Asset symbol

        Returns:
            True if refresh needed
        """
        if asset not in self.last_refresh:
            return True

        elapsed = (datetime.now(timezone.utc) - self.last_refresh[asset]).total_seconds()
        return elapsed >= self.refresh_interval_sec

    def calculate_order_levels(
        self,
        mid_price: float,
        directional_signal: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Calculate bid/ask price levels for market making.

        Args:
            mid_price: Current mid price
            directional_signal: Optional "buy"/"sell" signal from Trader XO

        Returns:
            Dict with "bids" and "asks" lists
        """
        bids = []
        asks = []

        # Calculate size skew based on directional signal
        bid_size_multiplier = 1.0
        ask_size_multiplier = 1.0

        if self.skew_on_signal and directional_signal:
            if directional_signal == "buy":
                # More aggressive on buy side
                bid_size_multiplier = 1.0 + self.skew_amount
                ask_size_multiplier = 1.0 - self.skew_amount
            elif directional_signal == "sell":
                # More aggressive on sell side
                ask_size_multiplier = 1.0 + self.skew_amount
                bid_size_multiplier = 1.0 - self.skew_amount

        for level in range(self.num_levels):
            # Calculate price offset
            offset_bps = self.spread_bps + (level * self.level_spacing_bps)

            # Bid (buy) level
            bid_price = mid_price * (1 - offset_bps / 10000)
            bid_size_usd = self.order_size_usd * bid_size_multiplier
            bid_size = bid_size_usd / mid_price

            bids.append({
                "price": bid_price,
                "size": bid_size,
                "size_usd": bid_size_usd,
                "level": level,
                "offset_bps": offset_bps
            })

            # Ask (sell) level
            ask_price = mid_price * (1 + offset_bps / 10000)
            ask_size_usd = self.order_size_usd * ask_size_multiplier
            ask_size = ask_size_usd / mid_price

            asks.append({
                "price": ask_price,
                "size": ask_size,
                "size_usd": ask_size_usd,
                "level": level,
                "offset_bps": offset_bps
            })

        return {
            "bids": bids,
            "asks": asks,
            "mid_price": mid_price,
            "directional_signal": directional_signal
        }

    def generate_market_making_plan(
        self,
        asset: str,
        mid_price: float,
        trader_xo_signal: Optional[Dict] = None
    ) -> Dict:
        """
        Generate market making plan for an asset.

        Args:
            asset: Asset symbol
            mid_price: Current mid price
            trader_xo_signal: Optional Trader XO analysis result

        Returns:
            Market making plan with order levels and metadata
        """
        # Extract directional signal if available
        directional_signal = None
        if trader_xo_signal and trader_xo_signal.get("signal") in ("buy", "sell"):
            directional_signal = trader_xo_signal["signal"]

        # Calculate order levels
        levels = self.calculate_order_levels(mid_price, directional_signal)

        # Build plan
        plan = {
            "asset": asset,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mid_price": mid_price,
            "directional_signal": directional_signal,
            "bids": levels["bids"],
            "asks": levels["asks"],
            "total_bid_size_usd": sum(b["size_usd"] for b in levels["bids"]),
            "total_ask_size_usd": sum(a["size_usd"] for a in levels["asks"]),
            "should_refresh": self.should_refresh(asset),
            "rationale": self._build_rationale(directional_signal, mid_price)
        }

        return plan

    def _build_rationale(self, directional_signal: Optional[str], mid_price: float) -> str:
        """Build human-readable rationale for MM plan."""
        parts = [
            f"Market making with {self.num_levels} levels, {self.spread_bps}bps spread"
        ]

        if directional_signal:
            parts.append(
                f"Directional bias: {directional_signal.upper()} "
                f"(skewing {'bid' if directional_signal == 'buy' else 'ask'} sizes by {self.skew_amount*100:.0f}%)"
            )
        else:
            parts.append("Neutral (no directional signal)")

        parts.append(f"Mid price: ${mid_price:.2f}")

        return ". ".join(parts)

    def mark_refreshed(self, asset: str):
        """Mark asset as refreshed."""
        self.last_refresh[asset] = datetime.now(timezone.utc)

    def combine_with_trader_xo(
        self,
        asset: str,
        mid_price: float,
        trader_xo_analysis: Dict
    ) -> Dict:
        """
        Combine market making with Trader XO signals for hybrid strategy.

        Args:
            asset: Asset symbol
            mid_price: Current mid price
            trader_xo_analysis: Trader XO analysis result

        Returns:
            Combined strategy plan
        """
        # Generate MM plan with directional bias
        mm_plan = self.generate_market_making_plan(
            asset, mid_price, trader_xo_analysis
        )

        # Add Trader XO context
        mm_plan["trader_xo_context"] = {
            "signal": trader_xo_analysis.get("signal"),
            "rationale": trader_xo_analysis.get("rationale"),
            "fast_ema": trader_xo_analysis.get("fast_ema"),
            "slow_ema": trader_xo_analysis.get("slow_ema"),
            "stop_loss": trader_xo_analysis.get("stop_loss"),
            "take_profit": trader_xo_analysis.get("take_profit")
        }

        # Build combined rationale
        combined_rationale = mm_plan["rationale"]
        if trader_xo_analysis.get("rationale"):
            combined_rationale += f" | Trader XO: {trader_xo_analysis['rationale']}"

        mm_plan["combined_rationale"] = combined_rationale

        return mm_plan

    def adjust_for_inventory(
        self,
        plan: Dict,
        current_position: float,
        max_position: float
    ) -> Dict:
        """
        Adjust order sizes based on current inventory to manage risk.

        Args:
            plan: Market making plan
            current_position: Current position size (positive = long)
            max_position: Maximum allowed position

        Returns:
            Adjusted plan
        """
        # Calculate inventory ratio (-1 to 1)
        if max_position == 0:
            return plan

        inventory_ratio = current_position / max_position

        # Adjust sizes
        # If heavily long (inventory_ratio > 0.5), reduce bid sizes and increase ask sizes
        # If heavily short (inventory_ratio < -0.5), increase bid sizes and reduce ask sizes
        if abs(inventory_ratio) > 0.3:
            adjustment = min(abs(inventory_ratio), 0.5)  # Cap at 50%

            if inventory_ratio > 0:  # Long
                # Reduce bids, increase asks
                for bid in plan["bids"]:
                    bid["size"] *= (1 - adjustment)
                    bid["size_usd"] *= (1 - adjustment)
                for ask in plan["asks"]:
                    ask["size"] *= (1 + adjustment)
                    ask["size_usd"] *= (1 + adjustment)

                plan["inventory_adjustment"] = f"Long position ({current_position:.4f}): reducing bids, increasing asks"

            else:  # Short
                # Increase bids, reduce asks
                for bid in plan["bids"]:
                    bid["size"] *= (1 + adjustment)
                    bid["size_usd"] *= (1 + adjustment)
                for ask in plan["asks"]:
                    ask["size"] *= (1 - adjustment)
                    ask["size_usd"] *= (1 - adjustment)

                plan["inventory_adjustment"] = f"Short position ({current_position:.4f}): increasing bids, reducing asks"

            # Recalculate totals
            plan["total_bid_size_usd"] = sum(b["size_usd"] for b in plan["bids"])
            plan["total_ask_size_usd"] = sum(a["size_usd"] for a in plan["asks"])

        return plan
