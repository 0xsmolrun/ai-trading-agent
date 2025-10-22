# Trader XO Strategy Documentation

## Overview

The **Trader XO Strategy** is a technical analysis-based trading strategy originally created by [@btc_charlie](https://www.tradingview.com/u/btc_charlie/) for TradingView Pine Script. This implementation adapts the strategy for the AI Trading Agent on Hyperliquid.

The strategy uses **dual EMA crossovers** as primary entry/exit signals, with optional **Stochastic RSI confirmation** and a **Moving Average filter** to ensure trades align with the broader trend.

---

## Strategy Components

### 1. Dual EMA System

The core of the strategy is a **Fast EMA** and **Slow EMA** crossover system:

- **Fast EMA (default: 12 periods)**: Responds quickly to price changes
- **Slow EMA (default: 25 periods)**: Provides trend direction

**Trading Signals**:
- **Buy Signal**: Fast EMA crosses **above** Slow EMA (bullish crossover)
- **Sell Signal**: Fast EMA crosses **below** Slow EMA (bearish crossover)

The strategy includes **signal filtering** to prevent repeated signals on the same crossover by tracking buy/sell counts.

### 2. Moving Average Filter (Optional)

A **long-period Moving Average** (default: 200 periods) acts as a trend filter:

- **For Buy signals**: Price must be **above** the MA filter
- **For Sell signals**: Price must be **below** the MA filter

Supported MA types:
- **EMA** (Exponential Moving Average) - default
- **SMA** (Simple Moving Average)
- **WMA** (Weighted Moving Average)
- **None** (disables the filter)

This filter helps avoid counter-trend trades in choppy or ranging markets.

### 3. Stochastic RSI (Optional)

The **Stochastic RSI** provides momentum confirmation:

- **K Period**: 3 (default)
- **D Period**: 3 (default)
- **RSI Length**: 14 (default)
- **Stochastic Length**: 14 (default)

**Bands**:
- Upper Band: 80 (overbought)
- Middle Band: 50 (neutral)
- Lower Band: 20 (oversold)

**Confirmation Logic** (when enabled):
- **Buy**: K crosses above D in oversold/neutral zone (K or D < 50)
- **Sell**: K crosses below D in overbought/neutral zone (K or D > 50)

### 4. Risk Management

**Stop Loss**:
- **Configurable percentage-based stops** (default: 7%)
- For **long positions**: Stop at `entry_price × (1 - stop_loss_percent / 100)`
- For **short positions**: Stop at `entry_price × (1 + stop_loss_percent / 100)`

**Take Profit**:
- **Automatically calculated** at 2:1 risk-reward ratio
- For **long**: TP = `entry_price + (risk × 2)`
- For **short**: TP = `entry_price - (risk × 2)`

**Exit Plan**:
- Positions are **closed on opposite EMA crossover**
- Stop Loss and Take Profit orders are placed on entry

---

## Configuration

### Environment Variables

Add these to your `.env` file to enable and configure the Trader XO Strategy:

```bash
# Enable strategy-based trading
USE_STRATEGY=true

# Strategy name (currently only "trader_xo" is supported)
STRATEGY_NAME=trader_xo

# Strategy mode: "standalone" or "hybrid"
STRATEGY_MODE=standalone

# Trader XO Strategy Parameters
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_PERIOD=200
TRADER_XO_MA_FILTER_TYPE=EMA  # EMA, SMA, WMA, or None
TRADER_XO_STOP_LOSS_PERCENT=7.0
TRADER_XO_USE_STOP_LOSS=true
TRADER_XO_USE_STOCH_CONFIRMATION=false
```

### Strategy Modes

#### 1. **Standalone Mode** (Recommended)
```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
```

- The strategy operates **independently** without LLM involvement
- **Faster execution** (no LLM API calls)
- **More predictable** and transparent decision-making
- **Lower costs** (no OpenRouter API usage)
- Ideal for **pure technical analysis** trading

#### 2. **Hybrid Mode**
```bash
USE_STRATEGY=true
STRATEGY_MODE=hybrid
```

- Strategy indicators are **added to the LLM context**
- LLM makes final decisions with **strategy signals as input**
- Combines **technical analysis with AI reasoning**
- Useful for **complex market conditions** requiring discretion
- Higher API costs due to LLM usage

#### 3. **LLM-Only Mode** (Original)
```bash
USE_STRATEGY=false
```

- **Disables strategy**, uses original LLM-based decision making
- LLM analyzes indicators and makes all decisions
- Most flexible but less predictable

---

## Usage Examples

### Example 1: Conservative Trading (EMA + MA Filter)

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_TYPE=EMA
TRADER_XO_MA_FILTER_PERIOD=200
TRADER_XO_STOP_LOSS_PERCENT=5.0
TRADER_XO_USE_STOP_LOSS=true
TRADER_XO_USE_STOCH_CONFIRMATION=false
```

**Profile**:
- Only trades when price is trending with 200 EMA
- Tighter 5% stop loss
- Good for trending markets

### Example 2: Aggressive Momentum Trading

```bash
USE_STRATEGY=true
STRATEGY_MODE=standalone
TRADER_XO_FAST_EMA=8
TRADER_XO_SLOW_EMA=21
TRADER_XO_MA_FILTER_TYPE=None
TRADER_XO_STOP_LOSS_PERCENT=10.0
TRADER_XO_USE_STOP_LOSS=true
TRADER_XO_USE_STOCH_CONFIRMATION=true
```

**Profile**:
- Faster EMAs (8/21) for quicker signals
- No MA filter - trades all crossovers
- Requires Stochastic RSI momentum confirmation
- Wider 10% stop for volatility

### Example 3: Hybrid Mode with AI Oversight

```bash
USE_STRATEGY=true
STRATEGY_MODE=hybrid
TRADER_XO_FAST_EMA=12
TRADER_XO_SLOW_EMA=25
TRADER_XO_MA_FILTER_TYPE=EMA
TRADER_XO_MA_FILTER_PERIOD=200
TRADER_XO_STOP_LOSS_PERCENT=7.0
TRADER_XO_USE_STOCH_CONFIRMATION=false
```

**Profile**:
- Strategy provides technical signals
- LLM evaluates signals with market context
- Can override strategy during abnormal conditions
- Best of both worlds

---

## Strategy Logic Flow

```
1. FETCH MARKET DATA
   ├─ Current price
   ├─ Historical prices (250+ candles for 200 MA)
   └─ Calculate EMAs

2. CALCULATE INDICATORS
   ├─ Fast EMA (e.g., 12-period)
   ├─ Slow EMA (e.g., 25-period)
   ├─ MA Filter (e.g., 200-period EMA)
   └─ [Optional] Stochastic RSI

3. DETECT CROSSOVERS
   ├─ Bullish: Fast EMA crosses above Slow EMA
   └─ Bearish: Fast EMA crosses below Slow EMA

4. APPLY FILTERS
   ├─ MA Filter: Check price vs 200 MA
   ├─ Signal Counter: Prevent repeat signals
   └─ [Optional] StochRSI Confirmation

5. GENERATE SIGNAL
   ├─ BUY: Bullish cross + filters pass
   ├─ SELL: Bearish cross + filters pass
   └─ HOLD: No crossover or filters fail

6. CALCULATE STOPS & TARGETS
   ├─ Stop Loss: entry_price ± stop_loss_percent
   └─ Take Profit: entry_price ± (risk × 2)

7. EXECUTE TRADE
   ├─ Place market order
   ├─ Set TP trigger order
   ├─ Set SL trigger order
   └─ Log to diary
```

---

## Performance Considerations

### Data Requirements

The strategy needs **sufficient historical data** for accurate indicator calculation:

- **Minimum candles**: `max(fast_ema, slow_ema, ma_filter_period) + 50`
- For **200-period MA filter**: At least **250 candles**
- TAAPI provides historical data via `fetch_series`

### Computational Efficiency

- **EMA calculation**: O(n) where n = number of candles
- **Stochastic RSI**: O(n × m) where m = lookback periods
- **MA filter**: O(n)

**Recommendation**: Use TAAPI API for indicator fetching when possible (already implemented).

### Trade Frequency

Frequency depends on:
- **Interval**: Lower intervals (5m) = more signals
- **EMA periods**: Faster EMAs (8/21) = more crossovers
- **MA filter**: Stricter filtering = fewer trades
- **Market volatility**: Higher volatility = more crossovers

**Example** (BTC, 5-minute interval, 12/25 EMA):
- **Trending market**: 5-10 signals per day
- **Ranging market**: 1-3 signals per day (with 200 MA filter)

---

## Troubleshooting

### Issue: "Insufficient price data"

**Cause**: Not enough historical candles for indicator calculation

**Solution**:
```python
# Ensure TAAPI fetches enough data
results = 250  # For 200-period MA + buffer
```

### Issue: No signals generated

**Possible causes**:
1. **MA filter too strict**: Try `TRADER_XO_MA_FILTER_TYPE=None`
2. **No crossovers**: Market is ranging or trend is established
3. **StochRSI confirmation failing**: Disable with `TRADER_XO_USE_STOCH_CONFIRMATION=false`

**Debug**: Check logs for rationale messages:
```
BUY signal filtered out: price below EMA(200)
```

### Issue: Too many signals

**Solutions**:
1. **Enable MA filter**: `TRADER_XO_MA_FILTER_TYPE=EMA`
2. **Use longer EMAs**: Increase `TRADER_XO_FAST_EMA` and `TRADER_XO_SLOW_EMA`
3. **Enable StochRSI confirmation**: `TRADER_XO_USE_STOCH_CONFIRMATION=true`

---

## Code Structure

### Files

```
src/strategies/
├── __init__.py                    # Package initializer
├── trader_xo.py                   # Core strategy implementation
└── strategy_integration.py        # Integration with trading agent
```

### Key Classes

#### `TraderXOStrategy` (trader_xo.py)

**Methods**:
- `calculate_ema()`: Compute EMA from price series
- `calculate_sma()`: Compute Simple Moving Average
- `calculate_wma()`: Compute Weighted Moving Average
- `calculate_rsi()`: Compute RSI for Stochastic RSI
- `calculate_stochastic_rsi()`: Compute StochRSI with K/D
- `check_ma_filter()`: Validate trade against MA filter
- `analyze()`: **Main analysis method** - returns signal dict

#### `StrategyIntegration` (strategy_integration.py)

**Methods**:
- `generate_trade_decisions()`: Generate decisions for multiple assets
- `format_strategy_context()`: Format indicators for LLM (hybrid mode)

---

## Comparison with Original Pine Script

### Implemented Features ✅

- ✅ Dual EMA system (Fast/Slow)
- ✅ EMA crossover detection
- ✅ Signal counting to prevent repeats
- ✅ Moving Average filter (EMA/SMA/WMA)
- ✅ Stochastic RSI calculation
- ✅ Stop Loss (percentage-based)
- ✅ Take Profit (risk-reward ratio)

### Not Implemented (Visual Only in Pine Script) ❌

- ❌ Monthly Open/Close support/resistance lines
- ❌ Monday Open/Close support/resistance lines
- ❌ Background color alerts
- ❌ Visual bar coloring

**Reason**: These are **visual indicators** for charting and not used in trading logic. They can be added to a charting frontend if needed.

### Enhancements Over Original 🚀

- 🚀 **Modular design**: Easy to extend and customize
- 🚀 **TAAPI integration**: Uses professional indicator API
- 🚀 **Hybrid mode**: Combines strategy with LLM reasoning
- 🚀 **Dynamic allocation**: Splits capital across active signals
- 🚀 **Multi-asset support**: Analyzes and trades multiple assets simultaneously
- 🚀 **Comprehensive logging**: Tracks all decisions in diary
- 🚀 **Live execution**: Automated order placement on Hyperliquid

---

## Best Practices

### 1. Backtesting

Before using real funds:
1. Enable strategy in **paper trading mode**
2. Monitor diary entries for signal quality
3. Analyze Sharpe ratio and win rate
4. Adjust parameters based on results

### 2. Parameter Tuning

**EMA Periods**:
- **Shorter (8/21)**: More signals, more noise
- **Longer (20/50)**: Fewer signals, stronger trends
- **Default (12/25)**: Good balance for most markets

**MA Filter**:
- **200 EMA**: Industry standard for long-term trend
- **50/100 EMA**: Medium-term trend
- **None**: Trade all crossovers (risky in ranging markets)

**Stop Loss**:
- **Tight (3-5%)**: Limits losses but may get stopped out frequently
- **Moderate (7-10%)**: Balanced approach
- **Wide (>10%)**: Allows for volatility but higher risk

### 3. Risk Management

- **Position sizing**: Use 90% of available balance, split across signals
- **Diversification**: Trade multiple uncorrelated assets
- **Leverage**: Keep leverage ≤ 5× (agent limit)
- **Monitoring**: Check diary and logs regularly

### 4. Market Conditions

**Best for**:
- ✅ Trending markets (strong directional moves)
- ✅ Low-to-moderate volatility
- ✅ Liquid assets (BTC, ETH, SOL)

**Avoid**:
- ❌ Extreme volatility (whipsaws)
- ❌ Low liquidity assets (wide spreads)
- ❌ News-driven flash crashes

---

## Support and Contributions

### Reporting Issues

If you encounter bugs or unexpected behavior:
1. Check logs in `diary.jsonl` and `prompts.log`
2. Verify configuration in `.env`
3. Open an issue with:
   - Configuration used
   - Asset and interval
   - Error logs
   - Expected vs actual behavior

### Contributing

To add new strategies or improve the Trader XO strategy:

1. **Fork the repository**
2. **Create a new strategy** in `src/strategies/`
3. **Implement the interface** (same as `TraderXOStrategy`)
4. **Update `strategy_integration.py`** to support new strategy
5. **Add configuration** to `config_loader.py`
6. **Submit a pull request**

---

## References

- **Original Pine Script**: [TradingView - @btc_charlie](https://www.tradingview.com/script/...)
- **EMA**: [Exponential Moving Average - Investopedia](https://www.investopedia.com/terms/e/ema.asp)
- **Stochastic RSI**: [StochRSI - TradingView](https://www.tradingview.com/support/solutions/43000502333-stochastic-rsi-stoch-rsi/)
- **TAAPI**: [Technical Analysis API](https://taapi.io/)
- **Hyperliquid**: [Hyperliquid DEX](https://hyperliquid.xyz/)

---

## License

This implementation is based on [@btc_charlie's Pine Script](https://www.tradingview.com/u/btc_charlie/), licensed under the **Mozilla Public License 2.0**.

**Modifications**:
- Adapted from Pine Script to Python
- Integrated with AI Trading Agent
- Added hybrid LLM mode
- Enhanced risk management

---

## Changelog

### v1.0.0 (2025-10-22)
- ✅ Initial implementation of Trader XO Strategy
- ✅ Dual EMA crossover system
- ✅ MA filter (EMA/SMA/WMA)
- ✅ Stochastic RSI confirmation
- ✅ Stop loss and take profit
- ✅ Standalone and hybrid modes
- ✅ Integration with Hyperliquid trading agent

---

**Happy Trading! 🚀**

For questions or support, please refer to the main [README.md](../README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
