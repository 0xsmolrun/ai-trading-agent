"""
Lighter DEX API Client

Lighter is a decentralized order book on Arbitrum that enables
limit order trading with on-chain settlement.

This client provides:
- Order placement and cancellation
- Position and balance queries
- Market making functionality
- Integration with Trader XO strategy
"""

import logging
from web3 import Web3
from eth_account import Account
from decimal import Decimal
import time
import json
from typing import Dict, List, Optional, Tuple
from src.config_loader import CONFIG


# Lighter V2 Router ABI (simplified - update with actual ABI)
LIGHTER_ROUTER_ABI = [
    {
        "inputs": [
            {"name": "orderBookId", "type": "uint8"},
            {"name": "amount0Base", "type": "uint64"},
            {"name": "priceBase", "type": "uint64"},
            {"name": "isAsk", "type": "bool"}
        ],
        "name": "createOrder",
        "outputs": [{"name": "orderId", "type": "uint32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "orderBookId", "type": "uint8"},
            {"name": "orderId", "type": "uint32"}
        ],
        "name": "cancelLimitOrder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "orderBookId", "type": "uint8"},
            {"name": "account", "type": "address"}
        ],
        "name": "getOrders",
        "outputs": [{"name": "", "type": "tuple[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "orderBookId", "type": "uint8"}
        ],
        "name": "getMidPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Order book IDs for different pairs
ORDER_BOOK_IDS = {
    "BTC": 0,
    "ETH": 1,
    "SOL": 2,
    "ARB": 3,
    # Add more as needed
}


class LighterAPI:
    """
    Lighter DEX API client for Arbitrum.

    Provides order placement, cancellation, and market making
    functionality for the Lighter decentralized order book.
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        router_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ):
        """
        Initialize Lighter API client.

        Args:
            rpc_url: Arbitrum RPC URL
            private_key: Wallet private key
            router_address: Lighter router contract address
            chain_id: Chain ID (42161 for Arbitrum mainnet)
        """
        self.rpc_url = rpc_url or CONFIG.get("lighter_rpc_url")
        self.private_key = private_key or CONFIG.get("lighter_private_key")
        self.router_address = router_address or CONFIG.get("lighter_router_address")
        self.chain_id = chain_id or CONFIG.get("lighter_chain_id", 42161)

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Arbitrum RPC: {self.rpc_url}")

        # Initialize account
        if self.private_key:
            if not self.private_key.startswith("0x"):
                self.private_key = "0x" + self.private_key
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
            logging.info(f"Lighter: Connected with address {self.address}")
        else:
            self.account = None
            self.address = None
            logging.warning("Lighter: No private key provided, read-only mode")

        # Initialize router contract
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.router_address),
            abi=LIGHTER_ROUTER_ABI
        )

        logging.info(f"Lighter API initialized on chain {self.chain_id}")

    def _get_order_book_id(self, asset: str) -> int:
        """Get order book ID for asset."""
        if asset not in ORDER_BOOK_IDS:
            raise ValueError(f"Unsupported asset: {asset}")
        return ORDER_BOOK_IDS[asset]

    def _price_to_base(self, price: float, decimals: int = 6) -> int:
        """Convert price to base units."""
        return int(price * (10 ** decimals))

    def _amount_to_base(self, amount: float, decimals: int = 18) -> int:
        """Convert amount to base units."""
        return int(amount * (10 ** decimals))

    def _base_to_price(self, price_base: int, decimals: int = 6) -> float:
        """Convert base units to price."""
        return float(price_base) / (10 ** decimals)

    def _base_to_amount(self, amount_base: int, decimals: int = 18) -> float:
        """Convert base units to amount."""
        return float(amount_base) / (10 ** decimals)

    async def get_current_price(self, asset: str) -> float:
        """
        Get current mid price for asset.

        Args:
            asset: Asset symbol (e.g., "BTC")

        Returns:
            Current mid price
        """
        try:
            order_book_id = self._get_order_book_id(asset)
            mid_price_base = self.router.functions.getMidPrice(order_book_id).call()
            return self._base_to_price(mid_price_base)
        except Exception as e:
            logging.error(f"Error getting price for {asset}: {e}")
            raise

    async def place_limit_order(
        self,
        asset: str,
        amount: float,
        price: float,
        is_ask: bool
    ) -> Dict:
        """
        Place a limit order.

        Args:
            asset: Asset symbol
            amount: Order size
            price: Limit price
            is_ask: True for sell, False for buy

        Returns:
            Order result dict with order_id
        """
        if not self.account:
            raise RuntimeError("Cannot place orders without private key")

        try:
            order_book_id = self._get_order_book_id(asset)
            amount_base = self._amount_to_base(amount)
            price_base = self._price_to_base(price)

            # Build transaction
            tx = self.router.functions.createOrder(
                order_book_id,
                amount_base,
                price_base,
                is_ask
            ).build_transaction({
                'from': self.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })

            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            # Extract order ID from logs (simplified)
            order_id = None
            if receipt['status'] == 1:
                # Parse logs to extract order ID
                # This is simplified - actual implementation needs log parsing
                order_id = int(time.time())  # Placeholder

            logging.info(
                f"Lighter: Placed {'SELL' if is_ask else 'BUY'} order for {amount} {asset} "
                f"at {price}, order_id={order_id}"
            )

            return {
                "success": receipt['status'] == 1,
                "order_id": order_id,
                "tx_hash": tx_hash.hex(),
                "gas_used": receipt['gasUsed']
            }

        except Exception as e:
            logging.error(f"Error placing limit order: {e}")
            raise

    async def place_buy_order(self, asset: str, amount: float, price: Optional[float] = None) -> Dict:
        """
        Place a buy order (limit at current market price if no price specified).

        Args:
            asset: Asset symbol
            amount: Order size
            price: Limit price (None for market-like order)

        Returns:
            Order result
        """
        if price is None:
            # Use current mid price with small buffer for immediate fill
            current_price = await self.get_current_price(asset)
            price = current_price * 1.001  # 0.1% above mid for quick fill

        return await self.place_limit_order(asset, amount, price, is_ask=False)

    async def place_sell_order(self, asset: str, amount: float, price: Optional[float] = None) -> Dict:
        """
        Place a sell order (limit at current market price if no price specified).

        Args:
            asset: Asset symbol
            amount: Order size
            price: Limit price (None for market-like order)

        Returns:
            Order result
        """
        if price is None:
            # Use current mid price with small buffer for immediate fill
            current_price = await self.get_current_price(asset)
            price = current_price * 0.999  # 0.1% below mid for quick fill

        return await self.place_limit_order(asset, amount, price, is_ask=True)

    async def cancel_order(self, asset: str, order_id: int) -> Dict:
        """
        Cancel a limit order.

        Args:
            asset: Asset symbol
            order_id: Order ID to cancel

        Returns:
            Cancellation result
        """
        if not self.account:
            raise RuntimeError("Cannot cancel orders without private key")

        try:
            order_book_id = self._get_order_book_id(asset)

            tx = self.router.functions.cancelLimitOrder(
                order_book_id,
                order_id
            ).build_transaction({
                'from': self.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })

            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            logging.info(f"Lighter: Cancelled order {order_id} for {asset}")

            return {
                "success": receipt['status'] == 1,
                "tx_hash": tx_hash.hex()
            }

        except Exception as e:
            logging.error(f"Error cancelling order: {e}")
            raise

    async def cancel_all_orders(self, asset: str) -> Dict:
        """
        Cancel all open orders for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Cancellation summary
        """
        open_orders = await self.get_open_orders(asset)
        cancelled_count = 0

        for order in open_orders:
            try:
                await self.cancel_order(asset, order['order_id'])
                cancelled_count += 1
            except Exception as e:
                logging.error(f"Failed to cancel order {order['order_id']}: {e}")

        return {"cancelled_count": cancelled_count}

    async def get_open_orders(self, asset: Optional[str] = None) -> List[Dict]:
        """
        Get open orders for asset or all assets.

        Args:
            asset: Asset symbol (None for all)

        Returns:
            List of open orders
        """
        if not self.address:
            return []

        try:
            orders = []
            assets = [asset] if asset else list(ORDER_BOOK_IDS.keys())

            for a in assets:
                order_book_id = self._get_order_book_id(a)
                raw_orders = self.router.functions.getOrders(
                    order_book_id,
                    self.address
                ).call()

                # Parse orders (simplified)
                for raw_order in raw_orders:
                    orders.append({
                        "coin": a,
                        "order_id": raw_order[0] if isinstance(raw_order, (list, tuple)) else 0,
                        "is_ask": raw_order[1] if isinstance(raw_order, (list, tuple)) else False,
                        "amount": self._base_to_amount(raw_order[2] if isinstance(raw_order, (list, tuple)) else 0),
                        "price": self._base_to_price(raw_order[3] if isinstance(raw_order, (list, tuple)) else 0),
                    })

            return orders

        except Exception as e:
            logging.error(f"Error getting open orders: {e}")
            return []

    async def get_user_state(self) -> Dict:
        """
        Get user balance and positions.

        Returns:
            Dict with balance and positions
        """
        if not self.address:
            return {"balance": 0, "positions": []}

        try:
            # Get ETH balance (used for gas and collateral)
            balance_wei = self.w3.eth.get_balance(self.address)
            balance = float(Web3.from_wei(balance_wei, 'ether'))

            # Get positions (simplified - would need actual position tracking)
            positions = []
            # TODO: Implement actual position tracking via events or subgraph

            return {
                "balance": balance,
                "positions": positions
            }

        except Exception as e:
            logging.error(f"Error getting user state: {e}")
            return {"balance": 0, "positions": []}

    # Market Making Functions

    async def place_market_making_orders(
        self,
        asset: str,
        mid_price: float,
        spread_bps: int = 10,
        order_size_usd: float = 100.0,
        num_levels: int = 3,
        level_spacing_bps: int = 5
    ) -> Dict:
        """
        Place market making orders (buy and sell) around mid price.

        Args:
            asset: Asset symbol
            mid_price: Current mid price
            spread_bps: Half-spread in basis points (default: 10 = 0.1%)
            order_size_usd: Order size in USD
            num_levels: Number of price levels on each side
            level_spacing_bps: Spacing between levels in bps

        Returns:
            Dict with placed order IDs
        """
        bid_orders = []
        ask_orders = []

        order_size = order_size_usd / mid_price  # Convert to asset amount

        for level in range(num_levels):
            # Calculate prices for this level
            offset_bps = spread_bps + (level * level_spacing_bps)
            bid_price = mid_price * (1 - offset_bps / 10000)
            ask_price = mid_price * (1 + offset_bps / 10000)

            # Place bid (buy) order
            try:
                bid_result = await self.place_limit_order(asset, order_size, bid_price, is_ask=False)
                if bid_result['success']:
                    bid_orders.append({
                        "order_id": bid_result['order_id'],
                        "price": bid_price,
                        "size": order_size,
                        "level": level
                    })
            except Exception as e:
                logging.error(f"Failed to place bid at level {level}: {e}")

            # Place ask (sell) order
            try:
                ask_result = await self.place_limit_order(asset, order_size, ask_price, is_ask=True)
                if ask_result['success']:
                    ask_orders.append({
                        "order_id": ask_result['order_id'],
                        "price": ask_price,
                        "size": order_size,
                        "level": level
                    })
            except Exception as e:
                logging.error(f"Failed to place ask at level {level}: {e}")

        logging.info(
            f"Lighter MM: Placed {len(bid_orders)} bids and {len(ask_orders)} asks for {asset}"
        )

        return {
            "bid_orders": bid_orders,
            "ask_orders": ask_orders,
            "mid_price": mid_price
        }

    async def refresh_market_making_orders(
        self,
        asset: str,
        spread_bps: int = 10,
        order_size_usd: float = 100.0,
        num_levels: int = 3,
        level_spacing_bps: int = 5
    ) -> Dict:
        """
        Cancel all orders and place fresh market making orders.

        Args:
            asset: Asset symbol
            spread_bps: Half-spread in basis points
            order_size_usd: Order size in USD
            num_levels: Number of price levels
            level_spacing_bps: Spacing between levels

        Returns:
            Dict with new order IDs
        """
        # Cancel all existing orders
        logging.info(f"Lighter MM: Cancelling existing orders for {asset}")
        await self.cancel_all_orders(asset)

        # Get current mid price
        mid_price = await self.get_current_price(asset)

        # Place new orders
        return await self.place_market_making_orders(
            asset, mid_price, spread_bps, order_size_usd, num_levels, level_spacing_bps
        )

    # Compatibility methods for Trader XO strategy

    async def place_take_profit(self, asset: str, is_buy: bool, amount: float, tp_price: float) -> Dict:
        """
        Place a take profit order (limit order at TP price).

        Args:
            asset: Asset symbol
            is_buy: True if original position was buy
            amount: Position size
            tp_price: Take profit price

        Returns:
            Order result
        """
        # For TP, we place opposite side order
        is_ask = is_buy  # If we bought, TP is a sell
        return await self.place_limit_order(asset, amount, tp_price, is_ask)

    async def place_stop_loss(self, asset: str, is_buy: bool, amount: float, sl_price: float) -> Dict:
        """
        Place a stop loss order.

        Note: Lighter doesn't have native stop orders, so this places a limit order.
        For true stop-loss, consider using a monitoring service.

        Args:
            asset: Asset symbol
            is_buy: True if original position was buy
            amount: Position size
            sl_price: Stop loss price

        Returns:
            Order result
        """
        # For SL, we place opposite side order
        is_ask = is_buy  # If we bought, SL is a sell
        logging.warning("Lighter: Stop-loss as limit order - consider using monitoring service")
        return await self.place_limit_order(asset, amount, sl_price, is_ask)

    def extract_oids(self, order_result: Dict) -> List:
        """Extract order IDs from order result (for compatibility)."""
        if order_result.get("order_id"):
            return [order_result["order_id"]]
        return []

    async def get_recent_fills(self, limit: int = 50) -> List[Dict]:
        """
        Get recent fills (trades).

        Note: This requires event parsing or subgraph integration.
        Returns empty list for now.

        Args:
            limit: Max number of fills

        Returns:
            List of fills
        """
        # TODO: Implement via event logs or subgraph
        logging.warning("Lighter: get_recent_fills not fully implemented yet")
        return []

    async def get_open_interest(self, asset: str) -> float:
        """Get open interest for asset (not applicable to Lighter, returns 0)."""
        return 0.0

    async def get_funding_rate(self, asset: str) -> float:
        """Get funding rate (not applicable to Lighter spot markets, returns 0)."""
        return 0.0
