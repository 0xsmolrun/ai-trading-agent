# What's New in AI Trading Agent

## 🎉 Major Updates

### 1. Multi-DEX Support

Trade on **Hyperliquid** or **Lighter DEX** with a simple configuration change!

```bash
# Switch DEXes instantly
DEX=hyperliquid  # or lighter
```

**Why Lighter?**
- ✅ Decentralized order book on Arbitrum
- ✅ Native market making support
- ✅ No funding rates (spot markets)
- ✅ Perfect for Trader XO strategy

### 2. Claude Sonnet 4.5 Support

Use the latest Claude model for AI-driven trading decisions!

```bash
LLM_MODEL=claude-sonnet-4.5
```

**Available Models**:
- `claude-sonnet-4.5` - 🆕 Latest and greatest
- `claude-sonnet-3.5` - Previous version
- `claude-opus-3.5` - Most capable
- `grok-4` - Fast and efficient (default)
- `gpt-4o` - OpenAI's best
- `deepseek-r1` - Cost-effective alternative

### 3. Multiple Timeframe Support

Run your strategy on any timeframe: **5m, 15m, 1h, 4h, 1d**

```bash
INTERVAL=15m  # 15-minute candles
```

**Supported**: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w

### 4. Market Making Strategy

Capture spread on Lighter DEX with automated market making!

```bash
LIGHTER_USE_MARKET_MAKING=true
MM_SPREAD_BPS=10                # 0.1% spread
MM_ORDER_SIZE_USD=100.0         # $100 per order
MM_NUM_LEVELS=3                 # 3 levels each side
```

**How it works**:
- Places tiered buy/sell orders around mid price
- Automatically refreshes orders
- Captures spread when filled
- Can combine with Trader XO for directional bias!

### 5. Hybrid Trading: Trader XO + Market Making

Get the best of both worlds - directional trading + liquidity provision!

```bash
# Enable both
USE_STRATEGY=true               # Trader XO
LIGHTER_USE_MARKET_MAKING=true  # Market Making
```

**Magic happens**:
- Trader XO detects trends (buy/sell signals)
- Market making applies **directional skew**
- Buy signal → More bid orders, fewer asks
- Sell signal → More ask orders, fewer bids
- Result: Accumulate position while earning spread!

---

## 🚀 Quick Start Examples

### Example 1: Claude Sonnet 4.5 on Hyperliquid

```bash
# .env
DEX=hyperliquid
LLM_MODEL=claude-sonnet-4.5
ASSETS="BTC ETH SOL"
INTERVAL=4h
```

### Example 2: Trader XO on Lighter (15m)

```bash
# .env
DEX=lighter
USE_STRATEGY=true
STRATEGY_MODE=standalone
ASSETS="BTC ETH"
INTERVAL=15m
```

### Example 3: Market Making on Lighter

```bash
# .env
DEX=lighter
LIGHTER_USE_MARKET_MAKING=true
USE_STRATEGY=false
ASSETS="BTC ETH SOL"
INTERVAL=5m

MM_SPREAD_BPS=10
MM_ORDER_SIZE_USD=100.0
```

### Example 4: Hybrid (Trader XO + Market Making)

```bash
# .env
DEX=lighter
USE_STRATEGY=true
LIGHTER_USE_MARKET_MAKING=true
ASSETS="BTC ETH"
INTERVAL=1h

# Trader XO params
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25

# Market making params
MM_SPREAD_BPS=15
MM_ORDER_SIZE_USD=150.0
MM_NUM_LEVELS=4
```

---

## 📚 New Documentation

1. **[MULTI_DEX_SETUP.md](docs/MULTI_DEX_SETUP.md)** - Complete multi-DEX guide
2. **[TRADER_XO_STRATEGY.md](docs/TRADER_XO_STRATEGY.md)** - Trader XO deep dive
3. **[TRADER_XO_QUICKSTART.md](TRADER_XO_QUICKSTART.md)** - 5-minute setup
4. **Updated [.env.example](.env.example)** - All new options

---

## 🔧 Configuration Reference

### DEX Selection

```bash
# Choose your DEX
DEX=hyperliquid  # Default
DEX=lighter      # New!
```

### LLM Models

```bash
# Short names (recommended)
LLM_MODEL=claude-sonnet-4.5
LLM_MODEL=grok-4
LLM_MODEL=gpt-4o

# Or full OpenRouter identifiers
LLM_MODEL=anthropic/claude-sonnet-4.5
LLM_MODEL=x-ai/grok-4
```

### Timeframes

```bash
# High frequency
INTERVAL=5m
INTERVAL=15m

# Swing trading
INTERVAL=1h
INTERVAL=4h

# Position trading
INTERVAL=1d
```

### Trader XO Strategy

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone  # or hybrid
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_TYPE=EMA
TRADER_XO_STOP_LOSS_PERCENT=7.0
```

### Market Making

```bash
LIGHTER_USE_MARKET_MAKING=true
MM_SPREAD_BPS=10                # 0.1% half-spread
MM_ORDER_SIZE_USD=100.0         # Order size
MM_NUM_LEVELS=3                 # Levels per side
MM_LEVEL_SPACING_BPS=5          # 0.05% between levels
MM_REFRESH_INTERVAL_SEC=30      # Refresh frequency
```

---

## 💡 Pro Tips

### 1. Match Timeframe to Strategy

- **Scalping (5m-15m)**: Use market making, tight stops
- **Day trading (1h)**: Trader XO with MA filter
- **Swing trading (4h-1d)**: Trader XO with longer EMAs

### 2. DEX Selection

- **Hyperliquid**: Leveraged directional trading
- **Lighter**: Market making, spot trading, lower risk

### 3. Hybrid Strategy Optimization

Combine Trader XO + MM for best results:
- Use 1h-4h timeframe for trend detection
- Apply 30% size skew on signal direction
- Set tight refresh intervals (30-45 sec)

### 4. Model Selection

- **Claude Sonnet 4.5**: Best reasoning, higher cost
- **Grok 4**: Fast, cost-effective, good performance
- **GPT-4o**: Balanced option

### 5. Start Conservative

```bash
# Day 1: Small sizes
MM_ORDER_SIZE_USD=10.0
TRADER_XO_STOP_LOSS_PERCENT=5.0

# After proving profitability: Scale up
MM_ORDER_SIZE_USD=100.0
TRADER_XO_STOP_LOSS_PERCENT=7.0
```

---

## 🏗️ Technical Details

### New Files

```
src/
├── trading/
│   └── lighter_api.py          # Lighter DEX client
├── strategies/
│   ├── trader_xo.py            # Trader XO strategy
│   ├── strategy_integration.py # Strategy bridge
│   └── market_making.py        # Market making strategy
└── config_loader.py            # Updated with new configs

docs/
├── MULTI_DEX_SETUP.md          # Multi-DEX guide
├── TRADER_XO_STRATEGY.md       # Strategy docs
└── WHATS_NEW.md                # This file!
```

### Key Features

- **Modular DEX architecture**: Easy to add more DEXes
- **Strategy composition**: Mix and match strategies
- **Unified interface**: Same code works on both DEXes
- **Flexible configuration**: Everything via .env

---

## 🔄 Migration Guide

### From Original Setup

**Before**:
```bash
HYPERLIQUID_PRIVATE_KEY=0x...
ASSETS="BTC ETH"
INTERVAL="5m"
LLM_MODEL="x-ai/grok-4"
```

**After** (no changes needed!):
```bash
# Automatically defaults to Hyperliquid
DEX=hyperliquid  # Optional, defaults to this
HYPERLIQUID_PRIVATE_KEY=0x...
ASSETS="BTC ETH"
INTERVAL="5m"
LLM_MODEL=grok-4  # Simplified name
```

**Backward compatible!** Old configurations still work.

### To Try Lighter

Add to existing .env:
```bash
DEX=lighter
LIGHTER_PRIVATE_KEY=0x_your_arbitrum_key
LIGHTER_RPC_URL=https://rpc.ankr.com/arbitrum
LIGHTER_ROUTER_ADDRESS=0x...  # Get from Lighter docs
```

### To Enable Market Making

Add to .env:
```bash
LIGHTER_USE_MARKET_MAKING=true
MM_SPREAD_BPS=10
MM_ORDER_SIZE_USD=100.0
MM_NUM_LEVELS=3
```

---

## 📊 Performance Comparison

### Hyperliquid (Original)

**Pros**:
- ✅ High leverage (up to 50x)
- ✅ Deep liquidity
- ✅ No gas costs
- ✅ Fast execution

**Cons**:
- ❌ Funding rate risk
- ❌ Perpetual futures only
- ❌ No native market making

### Lighter (New!)

**Pros**:
- ✅ True spot trading
- ✅ Native market making
- ✅ No funding rates
- ✅ On-chain settlement

**Cons**:
- ❌ Gas costs (minimal on Arbitrum)
- ❌ Lower leverage (spot 1x)
- ❌ Smaller liquidity

---

## ⚡ What's Next?

Planned features:
- [ ] Additional DEXes (Vertex, GMX)
- [ ] More strategies (Grid, DCA, Arbitrage)
- [ ] Portfolio optimization
- [ ] Backtesting framework
- [ ] Multi-agent coordination

---

## 🙋 Need Help?

- **📖 Docs**: See [docs/](docs/) for comprehensive guides
- **💬 Issues**: [GitHub Issues](https://github.com/0xsmolrun/ai-trading-agent/issues)
- **📧 Support**: Check README.md for contact info

---

**Built with ❤️ by the Trading Agent Team**

*Last updated: 2025-10-22*
