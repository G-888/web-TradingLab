import logging
import pandas as pd
from market.data import fetch_ohlcv

logger = logging.getLogger(__name__)

def run_rsi_mean_reversion_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
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

        # Calculate RSI (14)
        delta = df["Close"].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        df["RSI"] = 100 - (100 / (1 + rs))

        # Calculate ATR (14)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - df["Close"].shift()).abs()
        tr3 = (df["Low"] - df["Close"].shift()).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR"] = df["TR"].rolling(14).mean()
        
        trades = []
        position = 0 # 1 for Long, -1 for Short
        entry_price = 0.0
        entry_time = ""
        stop_loss = 0.0
        take_profit = 0.0
        
        for i in range(15, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # Skip if indicator values are NaN
            if pd.isna(prev["RSI"]) or pd.isna(curr["RSI"]) or pd.isna(curr["ATR"]):
                continue
                
            # Crossover logic
            cross_above_30 = prev["RSI"] < 30 and curr["RSI"] >= 30
            cross_below_70 = prev["RSI"] > 70 and curr["RSI"] <= 70
            
            # Hit SL / TP logic
            hit_sl_buy = position == 1 and curr["Low"] <= stop_loss
            hit_tp_buy = position == 1 and curr["High"] >= take_profit
            exit_buy_rsi = position == 1 and curr["RSI"] >= 50
            
            hit_sl_sell = position == -1 and curr["High"] >= stop_loss
            hit_tp_sell = position == -1 and curr["Low"] <= take_profit
            exit_sell_rsi = position == -1 and curr["RSI"] <= 50

            # Evaluate exits first
            if position == 1:
                if cross_below_70 or hit_sl_buy or hit_tp_buy or exit_buy_rsi:
                    exit_price = 0.0
                    reason = ""
                    if hit_sl_buy:
                        exit_price = stop_loss
                        reason = "Stop Loss Hit"
                    elif hit_tp_buy:
                        exit_price = take_profit
                        reason = "Take Profit Hit"
                    elif exit_buy_rsi:
                        exit_price = float(curr["Close"])
                        reason = "RSI Mean Reversion Reached 50"
                    elif cross_below_70:
                        exit_price = float(curr["Close"])
                        reason = "Opposite Signal"
                        
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
                if cross_above_30 or hit_sl_sell or hit_tp_sell or exit_sell_rsi:
                    exit_price = 0.0
                    reason = ""
                    if hit_sl_sell:
                        exit_price = stop_loss
                        reason = "Stop Loss Hit"
                    elif hit_tp_sell:
                        exit_price = take_profit
                        reason = "Take Profit Hit"
                    elif exit_sell_rsi:
                        exit_price = float(curr["Close"])
                        reason = "RSI Mean Reversion Reached 50"
                    elif cross_above_30:
                        exit_price = float(curr["Close"])
                        reason = "Opposite Signal"
                        
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
                if cross_above_30:
                    position = 1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    atr = float(curr["ATR"])
                    stop_loss = entry_price - (1.5 * atr)
                    take_profit = entry_price + (2.0 * atr)
                elif cross_below_70:
                    position = -1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    atr = float(curr["ATR"])
                    stop_loss = entry_price + (1.5 * atr)
                    take_profit = entry_price - (2.0 * atr)
                    
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
            "strategy_id": "rsi_mean_reversion",
            "strategy_name": "RSI Mean Reversion",
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
            "warnings": []
        }
        
    except Exception as e:
        logger.error(f"RSI Mean Reversion backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
