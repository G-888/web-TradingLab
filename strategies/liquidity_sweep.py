import logging
import pandas as pd
from market.data import fetch_ohlcv
from strategies.smc_components import detect_swing_points, detect_liquidity_sweep

logger = logging.getLogger(__name__)

def run_liquidity_sweep_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
    try:
        # Map dashboard lookback strings to yfinance periods
        period_map = {"7d": "1wk", "30d": "1mo", "90d": "3mo", "180d": "6mo", "1y": "1y"}
        period = period_map.get(lookback, "3mo")
        
        # Map dashboard timeframes to yfinance intervals
        tf_map = {"M5": "5m", "M15": "15m", "M30": "30m", "H1": "1h", "H4": "1d", "D1": "1d"} 
        interval = tf_map.get(timeframe, "1h")
        
        df = fetch_ohlcv(period, interval)
        if df is None or df.empty or len(df) < 50:
            return {"error": f"Insufficient data for {symbol} on {timeframe} over {lookback}."}

        # Calculate SMC components
        swings = detect_swing_points(df, window=5)
        sweeps = detect_liquidity_sweep(df, swings)
        
        # We need a quick lookup mapping for sweeps by their index
        sweep_map = {s["index"]: s for s in sweeps}

        trades = []
        position = 0 # 1 for Long, -1 for Short
        entry_price = 0.0
        entry_time = ""
        stop_loss = 0.0
        take_profit = 0.0
        
        for i in range(1, len(df)):
            curr = df.iloc[i]
            
            # Hit SL / TP logic
            hit_sl_buy = position == 1 and curr["Low"] <= stop_loss
            hit_tp_buy = position == 1 and curr["High"] >= take_profit
            hit_sl_sell = position == -1 and curr["High"] >= stop_loss
            hit_tp_sell = position == -1 and curr["Low"] <= take_profit

            # Evaluate exits
            if position == 1:
                if hit_sl_buy or hit_tp_buy:
                    exit_price = stop_loss if hit_sl_buy else take_profit
                    reason = "Stop Loss Hit" if hit_sl_buy else "Take Profit Hit"
                    pnl_pct = (exit_price - entry_price) / entry_price * 100
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": curr.name.isoformat(),
                        "direction": "BUY",
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "stop_loss": round(stop_loss, 2),
                        "take_profit": round(take_profit, 2),
                        "pnl": round(pnl_pct, 4),
                        "result": "WIN" if pnl_pct > 0 else ("LOSS" if pnl_pct < 0 else "BREAKEVEN"),
                        "reason": reason
                    })
                    position = 0
            
            elif position == -1:
                if hit_sl_sell or hit_tp_sell:
                    exit_price = stop_loss if hit_sl_sell else take_profit
                    reason = "Stop Loss Hit" if hit_sl_sell else "Take Profit Hit"
                    pnl_pct = (entry_price - exit_price) / entry_price * 100
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": curr.name.isoformat(),
                        "direction": "SELL",
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "stop_loss": round(stop_loss, 2),
                        "take_profit": round(take_profit, 2),
                        "pnl": round(pnl_pct, 4),
                        "result": "WIN" if pnl_pct > 0 else ("LOSS" if pnl_pct < 0 else "BREAKEVEN"),
                        "reason": reason
                    })
                    position = 0

            # Evaluate entries
            if position == 0:
                if i in sweep_map:
                    sweep = sweep_map[i]
                    
                    if sweep["direction"] == "bullish": # swept low, closed above -> buy setup
                        sl = float(curr["Low"]) # SL below the sweep wick
                        risk = float(curr["Close"]) - sl
                        # Filter out invalid or zero risk
                        if risk > 0 and risk < (curr["Close"] * 0.05): # Avoid massive volatility spikes
                            position = 1
                            entry_price = float(curr["Close"])
                            entry_time = curr.name.isoformat()
                            stop_loss = sl
                            take_profit = entry_price + (risk * 2.0)
                            
                    elif sweep["direction"] == "bearish": # swept high, closed below -> sell setup
                        sl = float(curr["High"]) # SL above the sweep wick
                        risk = sl - float(curr["Close"])
                        if risk > 0 and risk < (curr["Close"] * 0.05):
                            position = -1
                            entry_price = float(curr["Close"])
                            entry_time = curr.name.isoformat()
                            stop_loss = sl
                            take_profit = entry_price - (risk * 2.0)
                    
        # Calculate metrics
        total_trades = len(trades)
        if total_trades == 0:
            return {"error": "No trades generated in backtest period."}
            
        winning_trades = [t["pnl"] for t in trades if t["pnl"] > 0]
        losing_trades = [t["pnl"] for t in trades if t["pnl"] <= 0]
        
        win_rate = len(winning_trades) / total_trades
        
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum(losing_trades))
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else round(gross_profit, 2)
        
        # Max Drawdown estimation
        pnl_series = pd.Series([t["pnl"] for t in trades])
        cum_returns = pnl_series.cumsum()
        running_max = cum_returns.cummax()
        drawdown = cum_returns - running_max
        max_drawdown = round(abs(float(drawdown.min())), 2) if len(drawdown) > 0 else 0.0
        
        expectancy = round(sum([t["pnl"] for t in trades]) / total_trades, 2)
        net_pnl = round(sum([t["pnl"] for t in trades]), 2)
        
        # Approximate Risk-Reward from trades
        avg_win = gross_profit / len(winning_trades) if len(winning_trades) > 0 else 0
        avg_loss = gross_loss / len(losing_trades) if len(losing_trades) > 0 else 0
        avg_rr = round(avg_win / avg_loss, 2) if avg_loss > 0 else 0.0

        return {
            "strategy_id": "liquidity_sweep",
            "strategy_name": "Liquidity Sweep (SMC)",
            "symbol": symbol,
            "timeframe": timeframe,
            "lookback": lookback,
            "total_trades": total_trades,
            "wins": len(winning_trades),
            "losses": len(losing_trades),
            "win_rate": round(win_rate, 4),
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "net_pnl": net_pnl,
            "expectancy": expectancy,
            "sharpe": 0.0,
            "avg_rr": avg_rr,
            "score": 0.0,
            "trades": trades,
            "equity_curve": cum_returns.tolist(),
            "drawdown_curve": drawdown.tolist(),
            "warnings": [
                "Mechanical liquidity sweep approximation.",
                "SMC logic may differ by trader interpretation."
            ]
        }
        
    except Exception as e:
        logger.error(f"Liquidity Sweep backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
