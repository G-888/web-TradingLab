import logging
import pandas as pd
from market.data import fetch_ohlcv

logger = logging.getLogger(__name__)

def run_fibonacci_retracement_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
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

        # Find Swing Highs and Lows (window = 5)
        window = 5
        df["Swing_High"] = False
        df["Swing_Low"] = False
        
        for i in range(window, len(df) - window):
            is_high = True
            is_low = True
            for j in range(1, window + 1):
                if df["High"].iloc[i] <= df["High"].iloc[i-j] or df["High"].iloc[i] <= df["High"].iloc[i+j]:
                    is_high = False
                if df["Low"].iloc[i] >= df["Low"].iloc[i-j] or df["Low"].iloc[i] >= df["Low"].iloc[i+j]:
                    is_low = False
            if is_high:
                df.at[df.index[i], "Swing_High"] = True
            if is_low:
                df.at[df.index[i], "Swing_Low"] = True

        trades = []
        position = 0 # 1 for Long, -1 for Short
        entry_price = 0.0
        entry_time = ""
        stop_loss = 0.0
        take_profit = 0.0
        
        # Keep track of recent confirmed swings
        recent_highs = []
        recent_lows = []
        
        for i in range(window * 2, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # The swing point evaluated at i-window
            eval_idx = i - window
            eval_row = df.iloc[eval_idx]
            
            if eval_row["Swing_High"]:
                recent_highs.append({"price": float(eval_row["High"]), "idx": eval_idx, "time": eval_row.name})
                if len(recent_highs) > 5:
                    recent_highs.pop(0)
            if eval_row["Swing_Low"]:
                recent_lows.append({"price": float(eval_row["Low"]), "idx": eval_idx, "time": eval_row.name})
                if len(recent_lows) > 5:
                    recent_lows.pop(0)

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
            if position == 0 and len(recent_highs) >= 2 and len(recent_lows) >= 2:
                # Uptrend check: recent high > previous high AND recent low > previous low
                is_uptrend = recent_highs[-1]["price"] > recent_highs[-2]["price"] and recent_lows[-1]["price"] > recent_lows[-2]["price"]
                
                # Downtrend check: recent high < previous high AND recent low < previous low
                is_downtrend = recent_highs[-1]["price"] < recent_highs[-2]["price"] and recent_lows[-1]["price"] < recent_lows[-2]["price"]
                
                # We need the move connecting the latest high and latest low
                latest_high = recent_highs[-1]
                latest_low = recent_lows[-1]
                
                if is_uptrend and latest_low["idx"] < latest_high["idx"]: 
                    # impulsive move was low -> high
                    move_range = latest_high["price"] - latest_low["price"]
                    fib_38 = latest_high["price"] - (move_range * 0.382)
                    fib_61 = latest_high["price"] - (move_range * 0.618)
                    
                    # check if price is in fib zone (between 38.2 and 61.8)
                    # wait for a bullish candle closing in or above the zone
                    in_zone = fib_61 <= curr["Close"] <= fib_38 or fib_61 <= curr["Low"] <= fib_38
                    bullish_close = curr["Close"] > curr["Open"]
                    
                    if in_zone and bullish_close:
                        sl = latest_low["price"] - (move_range * 0.1) # sl slightly below swing low
                        risk = curr["Close"] - sl
                        if risk > 0:
                            position = 1
                            entry_price = float(curr["Close"])
                            entry_time = curr.name.isoformat()
                            stop_loss = sl
                            take_profit = entry_price + (risk * 2.0) # 2.0 RR
                
                elif is_downtrend and latest_high["idx"] < latest_low["idx"]:
                    # impulsive move was high -> low
                    move_range = latest_high["price"] - latest_low["price"]
                    fib_38 = latest_low["price"] + (move_range * 0.382)
                    fib_61 = latest_low["price"] + (move_range * 0.618)
                    
                    in_zone = fib_38 <= curr["Close"] <= fib_61 or fib_38 <= curr["High"] <= fib_61
                    bearish_close = curr["Close"] < curr["Open"]
                    
                    if in_zone and bearish_close:
                        sl = latest_high["price"] + (move_range * 0.1) # sl slightly above swing high
                        risk = sl - curr["Close"]
                        if risk > 0:
                            position = -1
                            entry_price = float(curr["Close"])
                            entry_time = curr.name.isoformat()
                            stop_loss = sl
                            take_profit = entry_price - (risk * 2.0) # 2.0 RR
                    
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
            "strategy_id": "fibonacci_retracement",
            "strategy_name": "Fibonacci Retracement",
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
                "Fibonacci logic is based on mechanical swing detection.",
                "Different swing settings may produce different results."
            ]
        }
        
    except Exception as e:
        logger.error(f"Fibonacci Retracement backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
