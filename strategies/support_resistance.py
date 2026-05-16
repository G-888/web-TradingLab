import logging
import pandas as pd
import numpy as np
from market.data import fetch_ohlcv

logger = logging.getLogger(__name__)

def run_support_resistance_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
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

        # Calculate ATR for tolerance/SL sizing
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - df["Close"].shift()).abs()
        tr3 = (df["Low"] - df["Close"].shift()).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR"] = df["TR"].rolling(14).mean()
        
        # Pre-calculate Swing Highs/Lows using simple rolling window (N=3)
        window = 3
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
        
        # Variables to track active levels dynamically
        support_levels = []
        resistance_levels = []
        
        for i in range(window * 2, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # Since swing points are only confirmed 'window' bars later, 
            # we evaluate a point at i-window if it's a swing point
            eval_idx = i - window
            eval_row = df.iloc[eval_idx]
            
            current_atr = curr["ATR"]
            if pd.isna(current_atr):
                continue
                
            tolerance = current_atr * 0.5 # Tolerance for clustering zones
            
            # Update levels
            if eval_row["Swing_High"]:
                lvl = eval_row["High"]
                matched = False
                for r in resistance_levels:
                    if abs(r["price"] - lvl) <= tolerance:
                        r["price"] = (r["price"] * r["touches"] + lvl) / (r["touches"] + 1)
                        r["touches"] += 1
                        matched = True
                        break
                if not matched:
                    resistance_levels.append({"price": lvl, "touches": 1, "time": eval_row.name})
                    
            if eval_row["Swing_Low"]:
                lvl = eval_row["Low"]
                matched = False
                for s in support_levels:
                    if abs(s["price"] - lvl) <= tolerance:
                        s["price"] = (s["price"] * s["touches"] + lvl) / (s["touches"] + 1)
                        s["touches"] += 1
                        matched = True
                        break
                if not matched:
                    support_levels.append({"price": lvl, "touches": 1, "time": eval_row.name})

            # Clean old/broken levels to avoid clustering madness
            support_levels = [s for s in support_levels if s["price"] < curr["Close"] + tolerance]
            resistance_levels = [r for r in resistance_levels if r["price"] > curr["Close"] - tolerance]

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
                buy_setup = False
                sell_setup = False
                
                # Check Support rejection
                for s in support_levels:
                    # if price touched zone and closed above
                    if curr["Low"] <= s["price"] + tolerance and curr["Close"] > s["price"]:
                        # Pinbar or strong rejection check (lower wick > 30% of candle)
                        body = abs(curr["Close"] - curr["Open"])
                        lower_wick = min(curr["Close"], curr["Open"]) - curr["Low"]
                        candle_range = curr["High"] - curr["Low"]
                        if candle_range > 0 and (lower_wick / candle_range > 0.3):
                            buy_setup = True
                            break
                            
                # Check Resistance rejection
                for r in resistance_levels:
                    if curr["High"] >= r["price"] - tolerance and curr["Close"] < r["price"]:
                        body = abs(curr["Close"] - curr["Open"])
                        upper_wick = curr["High"] - max(curr["Close"], curr["Open"])
                        candle_range = curr["High"] - curr["Low"]
                        if candle_range > 0 and (upper_wick / candle_range > 0.3):
                            sell_setup = True
                            break

                if buy_setup:
                    position = 1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    stop_loss = entry_price - (1.5 * current_atr)
                    # TP at 2.0 RR equivalent
                    take_profit = entry_price + (3.0 * current_atr) 
                elif sell_setup:
                    position = -1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    stop_loss = entry_price + (1.5 * current_atr)
                    take_profit = entry_price - (3.0 * current_atr)
                    
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
            "strategy_id": "support_resistance",
            "strategy_name": "Support and Resistance",
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
                "Support/resistance logic is a mechanical approximation.",
                "Performance highly depends on clustering tolerances and timeframe noise."
            ]
        }
        
    except Exception as e:
        logger.error(f"Support Resistance backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
