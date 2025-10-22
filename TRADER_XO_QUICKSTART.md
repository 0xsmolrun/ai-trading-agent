# Trader XO Strategy - Quick Start Guide

## What is the Trader XO Strategy?

A **technical analysis-based trading strategy** that uses **EMA crossovers** to generate buy/sell signals, originally created by [@btc_charlie](https://www.tradingview.com/u/btc_charlie/) for TradingView.

**Key Features**:
- 📈 **Dual EMA crossovers** (Fast 12 / Slow 25)
- 🛡️ **200-period MA trend filter**
- ⚡ **Automatic stop loss** (7% default)
- 🎯 **2:1 risk-reward take profit**
- 🤖 **Fully automated** on Hyperliquid

---

## 5-Minute Setup

### Step 1: Update Your `.env` File

Add these lines to your `.env`:

```bash
# Enable Trader XO Strategy
USE_STRATEGY=true
STRATEGY_NAME=trader_xo
STRATEGY_MODE=standalone
```

### Step 2: Run the Agent

```bash
poetry run python src/main.py --assets BTC ETH --interval 5m
```

**That's it!** The agent will now use the Trader XO strategy for all trading decisions.

---

## Configuration Options

### Basic Settings

```bash
# Enable/disable strategy
USE_STRATEGY=true

# Strategy mode
STRATEGY_MODE=standalone  # Options: standalone, hybrid
```

### Advanced Parameters

```bash
# EMA Periods
TRADER_XO_FAST_EMA=12       # Fast EMA (default: 12)
TRADER_XO_SLOW_EMA=25       # Slow EMA (default: 25)

# Trend Filter
TRADER_XO_MA_FILTER_PERIOD=200    # MA period (default: 200)
TRADER_XO_MA_FILTER_TYPE=EMA      # Type: EMA, SMA, WMA, None

# Risk Management
TRADER_XO_STOP_LOSS_PERCENT=7.0   # Stop loss % (default: 7%)
TRADER_XO_USE_STOP_LOSS=true      # Enable SL (default: true)

# Momentum Confirmation (Optional)
TRADER_XO_USE_STOCH_CONFIRMATION=false  # Require StochRSI (default: false)
```

---

## Strategy Modes

### 🚀 Standalone Mode (Recommended)

**Strategy makes all decisions independently**

```bash
STRATEGY_MODE=standalone
```

**Pros**:
- ✅ Faster (no LLM calls)
- ✅ Lower cost (no API usage)
- ✅ Predictable behavior
- ✅ Pure technical analysis

**Best for**: Systematic trading, backtesting, beginners

---

### 🧠 Hybrid Mode

**Strategy provides signals, LLM makes final decision**

```bash
STRATEGY_MODE=hybrid
```

**Pros**:
- ✅ Combines TA + AI reasoning
- ✅ Can adapt to market conditions
- ✅ Better for complex scenarios

**Cons**:
- ❌ Slower (LLM latency)
- ❌ Higher cost (OpenRouter API)

**Best for**: Advanced users, discretionary trading

---

## Example Configurations

### Conservative (Trending Markets)

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_TYPE=EMA
TRADER_XO_MA_FILTER_PERIOD=200
TRADER_XO_STOP_LOSS_PERCENT=5.0
```

**Profile**: Only trades with 200 EMA trend, tight 5% stop

---

### Aggressive (High Frequency)

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
TRADER_XO_FAST_EMA=8
TRADER_XO_SLOW_EMA=21
TRADER_XO_MA_FILTER_TYPE=None
TRADER_XO_STOP_LOSS_PERCENT=10.0
TRADER_XO_USE_STOCH_CONFIRMATION=true
```

**Profile**: Fast EMAs, no filter, StochRSI confirmation, wide stop

---

### Balanced (Default)

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
# Uses all defaults - no other config needed!
```

**Profile**: 12/25 EMA, 200 EMA filter, 7% stop

---

## How It Works

### Trading Logic

1. **Calculate Indicators**
   - Fast EMA (12-period)
   - Slow EMA (25-period)
   - 200 EMA trend filter

2. **Detect Crossovers**
   - **BUY**: Fast EMA crosses **above** Slow EMA
   - **SELL**: Fast EMA crosses **below** Slow EMA

3. **Apply Filters**
   - **Buy**: Price must be **above** 200 EMA
   - **Sell**: Price must be **below** 200 EMA

4. **Execute Trade**
   - Place market order
   - Set stop loss at entry ± 7%
   - Set take profit at 2:1 risk-reward

5. **Exit**
   - Opposite EMA crossover
   - Stop loss hit
   - Take profit hit

---

## Monitoring Your Trades

### View Diary

```bash
# Check recent trades
tail -f diary.jsonl | jq
```

### View Logs

```bash
# Check strategy decisions
tail -f prompts.log
```

### API Endpoints

```bash
# Recent diary entries
curl http://localhost:3000/diary?limit=20

# Agent logs
curl http://localhost:3000/logs?limit=100
```

---

## Troubleshooting

### ❌ No signals generated

**Solution**: Disable MA filter temporarily

```bash
TRADER_XO_MA_FILTER_TYPE=None
```

### ❌ Too many signals

**Solution**: Use longer EMAs or enable StochRSI

```bash
TRADER_XO_FAST_EMA=20
TRADER_XO_SLOW_EMA=50
# OR
TRADER_XO_USE_STOCH_CONFIRMATION=true
```

### ❌ "Insufficient price data" error

**Cause**: Not enough historical candles

**Solution**: Strategy automatically fetches 250 candles from TAAPI. If error persists, check TAAPI API key.

---

## Performance Tips

### Best Assets
- ✅ **BTC, ETH, SOL** (high liquidity)
- ✅ **Major altcoins** (BNB, AVAX, MATIC)
- ❌ Avoid low-cap / illiquid assets

### Best Timeframes
- **5m**: High frequency (5-10 signals/day)
- **15m**: Medium frequency (2-5 signals/day)
- **1h**: Low frequency (1-2 signals/day)

### Risk Management
- Use **multiple assets** for diversification
- Keep **leverage ≤ 3x** for strategy trades
- Monitor **Sharpe ratio** in diary

---

## Switching Back to LLM Mode

To disable the strategy and return to original LLM-based trading:

```bash
USE_STRATEGY=false
```

Or remove the lines from `.env` entirely.

---

## Next Steps

1. ✅ **Test in paper trading** first
2. 📊 **Monitor diary** for signal quality
3. 🔧 **Tune parameters** based on results
4. 📈 **Scale up** to real trading
5. 📚 **Read full docs**: [TRADER_XO_STRATEGY.md](docs/TRADER_XO_STRATEGY.md)

---

## Support

- **Full Documentation**: [docs/TRADER_XO_STRATEGY.md](docs/TRADER_XO_STRATEGY.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Issues**: [GitHub Issues](https://github.com/0xsmolrun/ai-trading-agent/issues)

---

**Happy Trading! 🚀**
