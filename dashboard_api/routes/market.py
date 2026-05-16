from fastapi import APIRouter, Depends, Query
from typing import Optional
from dashboard_api.auth import verify_api_key
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(verify_api_key)])

SYMBOL_MAPPING = {
    "XAUUSD": "GC=F",
    "NQ100": "NQ=F",
    "DJI30": "YM=F",
    "GBPJPY": "GBPJPY=X",
    "USDJPY": "JPY=X",
    "EURUSD": "EURUSD=X",
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "USOIL": "CL=F"
}

TIMEFRAME_MAPPING = {
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "H4": "1h",  # yf doesn't support 4h well natively for all lookbacks, might fallback to 1h
    "D1": "1d"
}

@router.get("/candles")
def get_market_candles(
    symbol: str = Query("XAUUSD", max_length=20),
    timeframe: str = Query("H1", max_length=10),
    limit: int = Query(300, ge=1, le=1000)
):
    """
    Fetch OHLCV candle data dynamically using yfinance.
    Returns format suitable for lightweight-charts:
    [{ time: unix_timestamp, open: number, high: number, low: number, close: number }]
    """
    if symbol not in SYMBOL_MAPPING:
        return []
    
    if timeframe not in TIMEFRAME_MAPPING:
        return []
        
    yf_symbol = SYMBOL_MAPPING[symbol]
    yf_interval = TIMEFRAME_MAPPING[timeframe]
    
    # Map timeframe to a safe period
    period = "60d"
    if timeframe in ["M5", "M15"]:
        period = "5d"
    elif timeframe in ["M30", "H1"]:
        period = "30d"
    elif timeframe == "D1":
        period = "2y"
        
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=yf_interval)
        
        if df.empty:
            return []
            
        # Limit to the requested number of candles
        df = df.tail(limit)
        
        candles = []
        for index, row in df.iterrows():
            # Convert timestamp to unix seconds
            unix_time = int(index.timestamp())
            candles.append({
                "time": unix_time,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
            
        return candles

    except Exception as e:
        logger.error(f"Error fetching candles for {symbol} {timeframe}: {str(e)}")
        return []
