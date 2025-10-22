# Multi-DEX Setup Guide

## Overview

The AI Trading Agent now supports **multiple DEXes** with flexible configuration:

- **Hyperliquid**: Perpetual futures on Arbitrum (original)
- **Lighter**: Decentralized order book on Arbitrum (NEW!)

Additionally, you can now:
- ✅ Use **Claude Sonnet 4.5** as your LLM
- ✅ Select from **multiple timeframes** (5m, 15m, 1h, 4h, 1d)
- ✅ Run **Market Making** on Lighter
- ✅ Combine **Trader XO + Market Making** for hybrid strategies

---

## Quick Start

### 1. Claude Sonnet 4.5 Setup

Simply set your LLM model in `.env`:

```bash
# Use Claude Sonnet 4.5
LLM_MODEL=claude-sonnet-4.5
```

**Supported Models**:
- `claude-sonnet-4.5` - Latest Claude model (NEW!)
- `claude-sonnet-3.5` - Previous Claude version
- `claude-opus-3.5` - Most capable Claude model
- `grok-4` - Grok 4 (default)
- `gpt-4o` - OpenAI GPT-4 Optimized
- `deepseek-r1` - DeepSeek R1

### 2. Timeframe Selection

Supported timeframes: **1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w**

```bash
# In .env
INTERVAL=15m  # 15-minute candles

# Or via CLI
python src/main.py --assets BTC ETH --interval 4h
```

### 3. DEX Selection

#### Option A: Hyperliquid (Default)

```bash
DEX=hyperliquid
HYPERLIQUID_PRIVATE_KEY=0x_your_key_here
```

#### Option B: Lighter DEX

```bash
DEX=lighter
LIGHTER_PRIVATE_KEY=0x_your_key_here
LIGHTER_RPC_URL=https://rpc.ankr.com/arbitrum
LIGHTER_ROUTER_ADDRESS=0x...  # Lighter V2 Router
```

---

## Lighter DEX Configuration

### What is Lighter?

**Lighter** is a decentralized order book on Arbitrum that enables:
- Limit order trading with on-chain settlement
- High capital efficiency
- No funding rates (spot markets)
- Market making opportunities

### Basic Setup

```bash
# .env configuration
DEX=lighter
LIGHTER_PRIVATE_KEY=0x_your_arbitrum_wallet_key
LIGHTER_RPC_URL=https://rpc.ankr.com/arbitrum
LIGHTER_CHAIN_ID=42161
LIGHTER_ROUTER_ADDRESS=0x...  # Get from Lighter docs
```

### Running Trader XO on Lighter

```bash
# Enable Trader XO strategy on Lighter
DEX=lighter
USE_STRATEGY=true
STRATEGY_MODE=standalone
INTERVAL=15m
ASSETS="BTC ETH SOL"
```

Run:
```bash
poetry run python src/main.py --assets BTC ETH --interval 15m
```

---

## Market Making Strategy

### Overview

The **Market Making Strategy** places buy and sell orders around the mid price to capture the spread. It's designed for Lighter's order book model.

### Basic Market Making

```bash
# .env
DEX=lighter
LIGHTER_USE_MARKET_MAKING=true

# Market making parameters
MM_SPREAD_BPS=10                # 0.1% spread (10 basis points)
MM_ORDER_SIZE_USD=100.0         # $100 per order
MM_NUM_LEVELS=3                 # 3 levels on each side
MM_LEVEL_SPACING_BPS=5          # 0.05% between levels
MM_REFRESH_INTERVAL_SEC=30      # Refresh every 30 seconds
```

**How it works**:
1. Places 3 buy orders below mid price (at -0.1%, -0.15%, -0.2%)
2. Places 3 sell orders above mid price (at +0.1%, +0.15%, +0.2%)
3. Refreshes orders every 30 seconds
4. Captures spread when orders are filled

### Market Making Configurations

#### Conservative (Wide Spread)

```bash
MM_SPREAD_BPS=20              # 0.2% spread
MM_ORDER_SIZE_USD=50.0        # Smaller size
MM_NUM_LEVELS=2               # Fewer levels
MM_REFRESH_INTERVAL_SEC=60    # Less frequent refreshes
```

- **Best for**: Volatile markets, risk-averse trading
- **Expected**: Lower fill rate, higher profit per trade

#### Aggressive (Tight Spread)

```bash
MM_SPREAD_BPS=5               # 0.05% spread
MM_ORDER_SIZE_USD=200.0       # Larger size
MM_NUM_LEVELS=5               # More levels
MM_REFRESH_INTERVAL_SEC=15    # Frequent refreshes
```

- **Best for**: Stable markets, high liquidity assets
- **Expected**: Higher fill rate, lower profit per trade

---

## Hybrid Strategy: Trader XO + Market Making

Combine **directional trading** (Trader XO) with **market making** for maximum performance!

### Setup

```bash
# .env
DEX=lighter
USE_STRATEGY=true
STRATEGY_MODE=standalone
LIGHTER_USE_MARKET_MAKING=true

# Trader XO parameters
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25

# Market making parameters
MM_SPREAD_BPS=10
MM_ORDER_SIZE_USD=100.0
MM_NUM_LEVELS=3
```

### How It Works

1. **Trader XO** analyzes market and generates buy/sell signals
2. **Market Making** applies **directional bias** to order sizes:
   - **Buy signal**: Increases bid sizes, reduces ask sizes (30% skew)
   - **Sell signal**: Increases ask sizes, reduces bid sizes (30% skew)
   - **Hold**: Symmetric market making (no skew)

3. **Result**: Capture spread while leaning into trends

### Example Scenario

**Market Condition**: BTC showing bullish EMA crossover

**Trader XO Signal**: `BUY`

**Market Making Adjustment**:
- Bid orders: 130% of normal size (more buying power)
- Ask orders: 70% of normal size (less selling)
- **Effect**: Accumulates BTC position while still providing liquidity

---

## Configuration Examples

### Example 1: Pure Market Making on Lighter

```bash
DEX=lighter
LIGHTER_USE_MARKET_MAKING=true
USE_STRATEGY=false

ASSETS="ETH BTC SOL"
INTERVAL=5m

MM_SPREAD_BPS=10
MM_ORDER_SIZE_USD=100.0
MM_NUM_LEVELS=3
MM_LEVEL_SPACING_BPS=5
MM_REFRESH_INTERVAL_SEC=30
```

**Profile**: Neutral market maker, no directional bias

---

### Example 2: Trader XO on Lighter (No MM)

```bash
DEX=lighter
USE_STRATEGY=true
STRATEGY_MODE=standalone
LIGHTER_USE_MARKET_MAKING=false

ASSETS="BTC ETH"
INTERVAL=15m

TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_TYPE=EMA
TRADER_XO_STOP_LOSS_PERCENT=7.0
```

**Profile**: Pure directional trading with EMA crossovers

---

### Example 3: Hybrid (Trader XO + Market Making)

```bash
DEX=lighter
USE_STRATEGY=true
STRATEGY_MODE=standalone
LIGHTER_USE_MARKET_MAKING=true

ASSETS="BTC ETH SOL"
INTERVAL=1h

# Trader XO
TRADER_XO_FAST_EMA=20
TRADER_XO_SLOW_EMA=50
TRADER_XO_MA_FILTER_PERIOD=200

# Market Making
MM_SPREAD_BPS=15
MM_ORDER_SIZE_USD=150.0
MM_NUM_LEVELS=4
MM_REFRESH_INTERVAL_SEC=45
```

**Profile**: Directional bias + liquidity provision

---

### Example 4: Claude Sonnet 4.5 on Hyperliquid

```bash
DEX=hyperliquid
LLM_MODEL=claude-sonnet-4.5
USE_STRATEGY=false

ASSETS="BTC ETH AVAX MATIC"
INTERVAL=4h
```

**Profile**: AI-driven trading with Claude Sonnet 4.5

---

### Example 5: Multi-Timeframe Trader XO

```bash
# 15-minute for quick signals
DEX=hyperliquid
USE_STRATEGY=true
INTERVAL=15m
TRADER_XO_FAST_EMA=8
TRADER_XO_SLOW_EMA=21

# Or 4-hour for swing trading
# INTERVAL=4h
# TRADER_XO_FAST_EMA=12
# TRADER_XO_SLOW_EMA=25
```

**Profile**: Scalping vs swing trading timeframes

---

## Comparison: Hyperliquid vs Lighter

| Feature | Hyperliquid | Lighter |
|---------|-------------|---------|
| **Market Type** | Perpetual Futures | Spot/Limit Orders |
| **Funding Rates** | Yes (hourly) | No |
| **Leverage** | Up to 50x | 1x (spot) |
| **Settlement** | Off-chain | On-chain (Arbitrum) |
| **Market Making** | Not native | Native (order book) |
| **Gas Costs** | None (off-chain) | Low (Arbitrum) |
| **Trader XO Strategy** | ✅ Supported | ✅ Supported |
| **Stop Loss/TP** | Native triggers | Limit orders |
| **Best For** | Leveraged directional trading | Market making, spot trading |

---

## Supported Timeframes

| Timeframe | Description | Best For |
|-----------|-------------|----------|
| **1m, 5m** | High frequency | Scalping, market making |
| **15m, 30m** | Medium frequency | Day trading |
| **1h, 2h, 4h** | Swing trading | Trend following |
| **1d, 1w** | Long-term | Position trading |

**Note**: Market making on Lighter works best with **5m-15m intervals** for active rebalancing.

---

## Running the Agent

### Hyperliquid with Claude Sonnet 4.5

```bash
poetry run python src/main.py --assets BTC ETH --interval 1h
```

### Lighter with Market Making

```bash
# Ensure .env is configured with DEX=lighter and LIGHTER_USE_MARKET_MAKING=true
poetry run python src/main.py --assets BTC ETH SOL --interval 5m
```

### Lighter with Trader XO + MM

```bash
# Both USE_STRATEGY=true and LIGHTER_USE_MARKET_MAKING=true in .env
poetry run python src/main.py --assets BTC --interval 15m
```

---

## Monitoring

### Check Logs

```bash
# Main agent log
tail -f prompts.log

# Trading diary
tail -f diary.jsonl | jq
```

### API Endpoints

```bash
# Recent trades
curl http://localhost:3000/diary?limit=20

# Agent logs
curl http://localhost:3000/logs?limit=100
```

---

## Troubleshooting

### Issue: "Failed to connect to Arbitrum RPC"

**Solution**: Update RPC URL in `.env`
```bash
LIGHTER_RPC_URL=https://arb1.arbitrum.io/rpc
# Or use Alchemy/Infura
LIGHTER_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Issue: Market making orders not filling

**Possible causes**:
1. **Spread too wide**: Reduce `MM_SPREAD_BPS`
2. **Order size too large**: Reduce `MM_ORDER_SIZE_USD`
3. **Refresh interval too short**: Increase `MM_REFRESH_INTERVAL_SEC`

### Issue: High gas costs on Lighter

**Solution**:
- Increase `MM_REFRESH_INTERVAL_SEC` to reduce transaction frequency
- Reduce `MM_NUM_LEVELS` to place fewer orders

### Issue: Claude Sonnet 4.5 not available

**Solution**: Check OpenRouter availability
```bash
# Fallback to Claude 3.5 Sonnet
LLM_MODEL=claude-sonnet-3.5
```

---

## Best Practices

### 1. Start Small

Test with small order sizes first:
```bash
MM_ORDER_SIZE_USD=10.0  # Start with $10
```

### 2. Monitor Performance

Track fill rate and profitability in diary.jsonl:
- **High fill rate + low profit**: Spread too tight
- **Low fill rate + high profit**: Spread too wide
- **Target**: 30-50% fill rate with 0.1-0.2% profit per trade

### 3. Adjust Based on Market Conditions

**Volatile markets**: Wider spreads, fewer levels
**Stable markets**: Tighter spreads, more levels

### 4. Combine Strategies

Use Trader XO to avoid market making against strong trends:
- **Strong buy signal**: Reduce/pause ask orders
- **Strong sell signal**: Reduce/pause bid orders

---

## Advanced: Multi-Asset Market Making

Run different strategies per asset:

```bash
# BTC: Aggressive MM (high liquidity)
# ETH: Moderate MM
# SOL: Conservative MM (higher volatility)

ASSETS="BTC ETH SOL"
MM_SPREAD_BPS=10  # Will apply to all, can customize per-asset in code
```

To customize per asset, modify `src/strategies/market_making.py` to accept asset-specific parameters.

---

## Next Steps

1. ✅ **Configure** your preferred DEX and strategies in `.env`
2. 📊 **Test** with paper trading or small sizes
3. 📈 **Monitor** performance via diary and logs
4. 🔧 **Tune** parameters based on results
5. 🚀 **Scale** up once profitable

---

## Support

- **Full Strategy Docs**: [TRADER_XO_STRATEGY.md](TRADER_XO_STRATEGY.md)
- **Quick Start**: [TRADER_XO_QUICKSTART.md](../TRADER_XO_QUICKSTART.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Happy Trading on Multiple DEXes! 🚀**
