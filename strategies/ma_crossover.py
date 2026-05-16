import logging
import pandas as pd
from market.data import fetch_ohlcv

logger = logging.getLogger(__name__)

def run_ma_crossover_backtest(symbol: str, timeframe: str, lookback: str) -> dict:
    """
    Backtest adapter for Moving Average Crossover strategy.
    Fast EMA = 9, Slow EMA = 21.
    """
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

        # Calculate EMAs
        df["EMA_Fast"] = df["Close"].ewm(span=9, adjust=False).mean()
        df["EMA_Slow"] = df["Close"].ewm(span=21, adjust=False).mean()
        
        trades = []
        position = 0 # 1 for Long, -1 for Short
        entry_price = 0.0
        entry_time = ""
        
        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # Crossover logic
            cross_up = prev["EMA_Fast"] <= prev["EMA_Slow"] and curr["EMA_Fast"] > curr["EMA_Slow"]
            cross_down = prev["EMA_Fast"] >= prev["EMA_Slow"] and curr["EMA_Fast"] < curr["EMA_Slow"]
            
            if position == 0:
                if cross_up:
                    position = 1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
                elif cross_down:
                    position = -1
                    entry_price = float(curr["Close"])
                    entry_time = curr.name.isoformat()
            elif position == 1:
                if cross_down:
                    # Close Long
                    exit_price = float(curr["Close"])
                    pnl_pct = (exit_price - entry_price) / entry_price * 100
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": curr.name.isoformat(),
                        "direction": "BUY",
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "stop_loss": 0,
                        "take_profit": 0,
                        "pnl": round(pnl_pct, 4),
                        "result": "WIN" if pnl_pct > 0 else ("LOSS" if pnl_pct < 0 else "BREAKEVEN"),
                        "reason": "MA Crossover Down"
                    })
                    # Reverse to Short
                    position = -1
                    entry_price = exit_price
                    entry_time = curr.name.isoformat()
            elif position == -1:
                if cross_up:
                    # Close Short
                    exit_price = float(curr["Close"])
                    pnl_pct = (entry_price - exit_price) / entry_price * 100
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": curr.name.isoformat(),
                        "direction": "SELL",
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "stop_loss": 0,
                        "take_profit": 0,
                        "pnl": round(pnl_pct, 4),
                        "result": "WIN" if pnl_pct > 0 else ("LOSS" if pnl_pct < 0 else "BREAKEVEN"),
                        "reason": "MA Crossover Up"
                    })
                    # Reverse to Long
                    position = 1
                    entry_price = exit_price
                    entry_time = curr.name.isoformat()
                    
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
        
        return {
            "strategy_id": "moving_average_crossover",
            "strategy_name": "Moving Average Crossover",
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
            "avg_rr": 0.0,
            "score": 0.0,
            "trades": trades,
            "equity_curve": cum_returns.tolist(),
            "drawdown_curve": drawdown.tolist(),
            "warnings": []
        }
        
    except Exception as e:
        logger.error(f"MA Crossover backtest failed: {e}")
        return {"error": f"Internal adapter error: {str(e)}"}
