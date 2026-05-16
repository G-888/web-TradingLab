import logging
import pandas as pd
from typing import Any
from strategies.registry import get_strategy

logger = logging.getLogger(__name__)

def _create_placeholder_result(strategy: dict, symbol: str, timeframe: str, warning_msg: str) -> dict:
    """Create a standard neutral result for unmapped/planned strategies."""
    return {
        "strategy_id": strategy["id"],
        "strategy_name": strategy["name"],
        "status": strategy["status"],
        "symbol": symbol,
        "timeframe": timeframe,
        "direction": "NEUTRAL",
        "confidence": 0,
        "entry_zone": [],
        "stop_loss": None,
        "take_profit": [],
        "reason": f"Placeholder: {warning_msg}",
        "signals": [],
        "warnings": [warning_msg]
    }

def run_strategy(strategy_id: str, symbol: str = "XAUUSD", timeframe: str = "H1", candles: Any = None) -> dict:
    """
    Safely route execution to the appropriate strategy logic.
    Returns a standardized dictionary.
    Does NOT execute live trades.
    """
    strategy = get_strategy(strategy_id)
    if not strategy:
        return {
            "strategy_id": strategy_id,
            "strategy_name": "Unknown",
            "status": "disabled",
            "symbol": symbol,
            "timeframe": timeframe,
            "direction": "NEUTRAL",
            "confidence": 0,
            "reason": "Invalid strategy ID.",
            "warnings": ["Strategy ID not found in registry."]
        }

    if strategy["status"] in ["planned", "disabled"]:
        msg = f"Strategy '{strategy['name']}' is registered but currently {strategy['status']}."
        return _create_placeholder_result(strategy, symbol, timeframe, msg)

    # Convert candles to DataFrame if needed
    df = None
    if candles is not None:
        if isinstance(candles, pd.DataFrame):
            df = candles
        elif isinstance(candles, list):
            try:
                df = pd.DataFrame(candles)
                if "time" in df.columns:
                    df["Datetime"] = pd.to_datetime(df["time"], unit="s" if isinstance(df["time"].iloc[0], (int, float)) and df["time"].iloc[0] > 1e9 else None)
                    df.set_index("Datetime", inplace=True)
                # Capitalize columns for standard OHLCV
                for col in ["open", "high", "low", "close", "volume"]:
                    if col in df.columns:
                        df.rename(columns={col: col.capitalize()}, inplace=True)
            except Exception as e:
                logger.error(f"Failed to convert candles to DataFrame: {e}")
                df = None

    if df is None or df.empty:
        return _create_placeholder_result(strategy, symbol, timeframe, "Insufficient or invalid market data provided.")

    try:
        if strategy_id == "fibonacci_retracement":
            from strategies.fibonacci import run_fibonacci_analysis
            res = run_fibonacci_analysis(df)
            if res:
                direction = "BUY" if "bullish" in res["bias"].lower() else "SELL" if "bearish" in res["bias"].lower() else "NEUTRAL"
                return {
                    "strategy_id": strategy_id,
                    "strategy_name": strategy["name"],
                    "status": strategy["status"],
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "direction": direction,
                    "confidence": res.get("confluence_score", 50),
                    "entry_zone": [res.get("nearest_price")],
                    "stop_loss": res.get("invalidation"),
                    "take_profit": [res.get("target")],
                    "reason": f"Fibonacci {res.get('bias')} at {res.get('nearest_level')}.",
                    "signals": [],
                    "warnings": []
                }

        elif strategy_id == "smart_money_concepts":
            from strategies.smc import run_smc_analysis
            res = run_smc_analysis(df)
            if res:
                direction = "BUY" if res["overall_bias"] == "Bullish" else "SELL" if res["overall_bias"] == "Bearish" else "NEUTRAL"
                conf = 80 if direction != "NEUTRAL" else 50
                return {
                    "strategy_id": strategy_id,
                    "strategy_name": strategy["name"],
                    "status": strategy["status"],
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "direction": direction,
                    "confidence": conf,
                    "entry_zone": [res.get("key_ob_level")],
                    "stop_loss": None,
                    "take_profit": [],
                    "reason": f"SMC Bias: {res['overall_bias']}. Structure: {res['structure_bias']}.",
                    "signals": [],
                    "warnings": []
                }

        elif strategy_id == "session_breakout":
            from strategies.session import analyze_session
            # session strategy usually wants h1 and h4, we pass the same df for safety if we only have one
            res = analyze_session(df, df)
            if res:
                direction = "BUY" if res["session_bias"] == "Bullish" else "SELL" if res["session_bias"] == "Bearish" else "NEUTRAL"
                return {
                    "strategy_id": strategy_id,
                    "strategy_name": strategy["name"],
                    "status": strategy["status"],
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "direction": direction,
                    "confidence": res.get("continuation_pct", 50),
                    "entry_zone": [],
                    "stop_loss": None,
                    "take_profit": [],
                    "reason": f"Session: {res['current_session']}. Pattern: {res['pattern']}.",
                    "signals": [],
                    "warnings": []
                }

        # If it's partial/implemented but we haven't mapped it above:
        msg = f"Strategy '{strategy['name']}' is {strategy['status']} but lacks a mapped execution router function."
        return _create_placeholder_result(strategy, symbol, timeframe, msg)

    except Exception as e:
        logger.error(f"Error executing strategy {strategy_id}: {e}")
        return _create_placeholder_result(strategy, symbol, timeframe, f"Execution failed: {str(e)}")

    # Fallback
    return _create_placeholder_result(strategy, symbol, timeframe, "Analysis yielded no actionable results.")

def run_backtest_adapter(strategy_id: str, symbol: str, timeframe: str, lookback: str) -> dict:
    """
    Run the backtest adapter for a given strategy.
    Returns standard benchmark metrics if implemented.
    """
    strategy = get_strategy(strategy_id)
    if not strategy:
        return {"error": f"Strategy {strategy_id} not found in registry."}
        
    can_backtest = strategy.get("testability", {}).get("can_backtest") or strategy.get("readiness", {}).get("backtesting")
    if not can_backtest:
        return {"error": "No backtest adapter available."}
        
    # Placeholder for actual backtest adapter execution
    if strategy_id == "moving_average_crossover":
        from strategies.ma_crossover import run_ma_crossover_backtest
        return run_ma_crossover_backtest(symbol, timeframe, lookback)
    elif strategy_id == "rsi_mean_reversion":
        from strategies.rsi_mean_reversion import run_rsi_mean_reversion_backtest
        return run_rsi_mean_reversion_backtest(symbol, timeframe, lookback)

    elif strategy_id == "macd_momentum":
        from strategies.macd_momentum import run_macd_momentum_backtest
        return run_macd_momentum_backtest(symbol, timeframe, lookback)
    elif strategy_id == "bollinger_reversion":
        from strategies.bollinger_reversion import run_bollinger_reversion_backtest
        return run_bollinger_reversion_backtest(symbol, timeframe, lookback)
    elif strategy_id == "atr_volatility_strategy":
        from strategies.atr_volatility_strategy import run_atr_volatility_strategy_backtest
        return run_atr_volatility_strategy_backtest(symbol, timeframe, lookback)
    elif strategy_id == "support_resistance":
        from strategies.support_resistance import run_support_resistance_backtest
        return run_support_resistance_backtest(symbol, timeframe, lookback)
    elif strategy_id == "fibonacci_retracement":
        from strategies.fibonacci_retracement import run_fibonacci_retracement_backtest
        return run_fibonacci_retracement_backtest(symbol, timeframe, lookback)
    elif strategy_id == "liquidity_sweep":
        from strategies.liquidity_sweep import run_liquidity_sweep_backtest
        return run_liquidity_sweep_backtest(symbol, timeframe, lookback)
    elif strategy_id == "market_structure_break":
        from strategies.market_structure_break import run_market_structure_break_backtest
        return run_market_structure_break_backtest(symbol, timeframe, lookback)
    elif strategy_id == "fair_value_gap":
        from strategies.fair_value_gap import run_fair_value_gap_backtest
        return run_fair_value_gap_backtest(symbol, timeframe, lookback)

    return {"error": f"No backtest adapter available for {strategy_id}."}

def run_forward_test_adapter(strategy_id: str, symbol: str, timeframe: str, duration_days: int) -> dict:
    """
    Start a forward test session for a given strategy.
    """
    strategy = get_strategy(strategy_id)
    if not strategy or not strategy.get("testability", {}).get("can_forward_test"):
        return {"error": "No forward test adapter available."}
        
    # Placeholder for actual forward test adapter execution
    return {"error": "No forward test adapter available."}
