#!/usr/bin/env python3
"""
Test setup script for AI Trading Agent
Verifies configuration and dependencies
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("AI TRADING AGENT - SETUP TEST")
print("=" * 70)

# Test 1: Check .env file
print("\n1. Checking .env file...")
env_path = Path(".env")
if env_path.exists():
    print("   ✓ .env file found")
else:
    print("   ✗ .env file not found")
    sys.exit(1)

# Test 2: Load environment variables
print("\n2. Loading environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✓ Environment variables loaded")
except Exception as e:
    print(f"   ✗ Error loading .env: {e}")
    sys.exit(1)

# Test 3: Check required API keys
print("\n3. Checking required API keys...")
taapi_key = os.getenv("TAAPI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if taapi_key and taapi_key != "your_taapi_key_here":
    print(f"   ✓ TAAPI_API_KEY: {taapi_key[:10]}...")
else:
    print("   ✗ TAAPI_API_KEY not configured")
    print("     Get your key from: https://taapi.io")

if openrouter_key and openrouter_key != "your_openrouter_key_here":
    print(f"   ✓ OPENROUTER_API_KEY: {openrouter_key[:10]}...")
else:
    print("   ✗ OPENROUTER_API_KEY not configured")
    print("     Get your key from: https://openrouter.ai")

# Test 4: Load configuration
print("\n4. Loading configuration...")
try:
    from src.config_loader import CONFIG, SUPPORTED_MODELS, SUPPORTED_TIMEFRAMES
    print("   ✓ Configuration loaded successfully")

    # Show configuration
    print(f"\n   Configuration Summary:")
    print(f"   - DEX: {CONFIG.get('dex', 'not set')}")
    print(f"   - LLM Model: {CONFIG.get('llm_model', 'not set')}")
    print(f"   - Assets: {CONFIG.get('assets', 'not set')}")
    print(f"   - Interval: {CONFIG.get('interval', 'not set')}")
    print(f"   - Strategy Enabled: {CONFIG.get('use_strategy', False)}")
    print(f"   - Strategy Mode: {CONFIG.get('strategy_mode', 'not set')}")

except Exception as e:
    print(f"   ✗ Error loading configuration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test imports
print("\n5. Testing module imports...")
modules_to_test = [
    ("TAAPI Client", "src.indicators.taapi_client", "TAAPIClient"),
    ("Hyperliquid API", "src.trading.hyperliquid_api", "HyperliquidAPI"),
    ("Lighter API", "src.trading.lighter_api", "LighterAPI"),
    ("Trading Agent", "src.agent.decision_maker", "TradingAgent"),
    ("Trader XO Strategy", "src.strategies.trader_xo", "TraderXOStrategy"),
    ("Market Making", "src.strategies.market_making", "MarketMakingStrategy"),
    ("Strategy Integration", "src.strategies.strategy_integration", "StrategyIntegration"),
]

all_imports_ok = True
for name, module_path, class_name in modules_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        getattr(module, class_name)
        print(f"   ✓ {name}")
    except Exception as e:
        print(f"   ✗ {name}: {e}")
        all_imports_ok = False

# Test 6: Verify supported models
print("\n6. Supported LLM Models:")
for short_name, full_name in SUPPORTED_MODELS.items():
    print(f"   - {short_name}: {full_name}")

# Test 7: Verify supported timeframes
print("\n7. Supported Timeframes:")
print(f"   {', '.join(SUPPORTED_TIMEFRAMES)}")

# Final summary
print("\n" + "=" * 70)
if taapi_key and taapi_key != "your_taapi_key_here" and \
   openrouter_key and openrouter_key != "your_openrouter_key_here" and \
   all_imports_ok:
    print("✓ SETUP COMPLETE - Ready to run!")
    print("=" * 70)
    print("\nTo start the agent, run:")
    print("  poetry run python src/main.py --assets BTC ETH --interval 5m")
    print("\nOr use the config from .env:")
    print("  poetry run python src/main.py")
    sys.exit(0)
else:
    print("⚠ SETUP INCOMPLETE")
    print("=" * 70)
    print("\nPlease complete the following:")
    if not taapi_key or taapi_key == "your_taapi_key_here":
        print("  1. Set TAAPI_API_KEY in .env (get from https://taapi.io)")
    if not openrouter_key or openrouter_key == "your_openrouter_key_here":
        print("  2. Set OPENROUTER_API_KEY in .env (get from https://openrouter.ai)")
    if not all_imports_ok:
        print("  3. Fix module import errors shown above")

    print("\nAfter configuration, run this test again:")
    print("  poetry run python test_setup.py")
    sys.exit(1)
