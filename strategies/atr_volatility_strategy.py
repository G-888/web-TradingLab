import logging
import pandas as pd
from market.data import fetch_ohlcv

logger = logging.getLogger(__name__)

def run_atr_volatility_strategy_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
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

        # Calculate ATR (14)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - df["Close"].shift()).abs()
        tr3 = (df["Low"] - df["Close"].shift()).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR"] = df["TR"].rolling(14).mean()
        df["ATR_MA"] = df["ATR"].rolling(14).mean()
        
        # Range logic (20 candles)
        df["Range_High"] = df["High"].rolling(20).max().shift(1)
        df["Range_Low"] = df["Low"].rolling(20).min().shift(1)
        
        trades = []
        position = 0 # 1 for Long, -1 for Short
        entry_price = 0.0
        entry_time = ""
        stop_loss = 0.0
        take_profit = 0.0
        bars_in_trade = 0
        MAX_BARS = 24
        
        for i in range(21, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            if pd.isna(curr["Range_High"]) or pd.isna(curr["ATR_MA"]):
                continue
                
            # Entry logic
            atr_breakout = curr["ATR"] > curr["ATR_MA"]
            buy_setup = atr_breakout and curr["Close"] > curr["Range_High"]
            sell_setup = atr_breakout and curr["Close"] < curr["Range_Low"]
            
            if position != 0:
                bars_in_trade += 1
            
            # Hit SL / TP logic
            hit_sl_buy = position == 1 and curr["Low"] <= stop_loss
            hit_tp_buy = position == 1 and curr["High"] >= take_profit
            timeout_buy = position == 1 and bars_in_trade >= MAX_BARS
            
            hit_sl_sell = position == -1 and curr["High"] >= stop_loss
            hit_tp_sell = position == -1 and curr["Low"] <= take_profit
            timeout_sell = position == -1 and bars_in_trade >= MAX_BARS

            # Evaluate exits
            if position == 1:
                if sell_setup or hit_sl_buy or hit_tp_buy or timeout_buy:
                    exit_price = 0.0
                    reason = ""
                    if hit_sl_buy:
                        exit_price = stop_loss
                        reason = "Stop Loss Hit"
                    elif hit_tp_buy:
                        exit_price = take_profit
                        reason = "Take Profit Hit"
                    elif sell_setup:
                        exit_price = float(curr["Close"])
                        reason = "Opposite Breakout"
                    elif timeout_buy:
                        exit_price = float(curr["Close"])
                        reason = f"Timeout ({MAX_BARS} candles)"
                        
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
                    bars_in_trade = 0
            
            elif position == -1:
                if buy_setup or hit_sl_sell or hit_tp_sell or timeout_sell:
                    exit_price = 0.0
                    reason = ""
                    if hit_sl_sell:
                        exit_price = stop_loss
                        reason = "Stop Loss Hit"
                    elif hit_tp_sell:
                        exit_price = take_profit
                        reason = "Take Profit Hit"
                    elif buy_setup:
                        exit_price = float(curr["Close"])
                        reason = "Opposite Breakout"
                    elif timeout_sell:
                        exit_price = float(curr["Close"])
                        reason = f"Timeout ({MAX_BARS} candles)"
                        
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
                    bars_in_trade = 0

            # Evaluate entries
            if position == 0:
                if buy_setup:
                    position = 1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    atr = float(curr["ATR"])
                    stop_loss = entry_price - (1.5 * atr)
                    take_profit = entry_price + (2.5 * atr)
                    bars_in_trade = 0
                elif sell_setup:
                    position = -1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                    atr = float(curr["ATR"])
                    stop_loss = entry_price + (1.5 * atr)
                    take_profit = entry_price - (2.5 * atr)
                    bars_in_trade = 0
                    
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
            "strategy_id": "atr_volatility_strategy",
            "strategy_name": "ATR Volatility Breakout",
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
        logger.error(f"ATR Volatility backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
