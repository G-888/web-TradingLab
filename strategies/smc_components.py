import pandas as pd
import numpy as np

def detect_swing_points(df: pd.DataFrame, window: int = 3) -> list[dict]:
    swings = []
    if len(df) < window * 2 + 1:
        return swings
        
    for i in range(window, len(df) - window):
        is_high = True
        is_low = True
        for j in range(1, window + 1):
            if df["High"].iloc[i] <= df["High"].iloc[i-j] or df["High"].iloc[i] <= df["High"].iloc[i+j]:
                is_high = False
            if df["Low"].iloc[i] >= df["Low"].iloc[i-j] or df["Low"].iloc[i] >= df["Low"].iloc[i+j]:
                is_low = False
                
        if is_high:
            swings.append({
                "type": "swing_high",
                "time": df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i]),
                "index": i,
                "price": float(df["High"].iloc[i]),
                "notes": f"Swing High (window={window})"
            })
        if is_low:
            swings.append({
                "type": "swing_low",
                "time": df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i]),
                "index": i,
                "price": float(df["Low"].iloc[i]),
                "notes": f"Swing Low (window={window})"
            })
            
    return swings

def detect_break_of_structure(df: pd.DataFrame, swing_points: list[dict]) -> list[dict]:
    bos_events = []
    # separate highs and lows
    highs = [s for s in swing_points if s["type"] == "swing_high"]
    lows = [s for s in swing_points if s["type"] == "swing_low"]
    
    if not highs and not lows:
        return bos_events
        
    for i in range(1, len(df)):
        curr_close = float(df["Close"].iloc[i])
        curr_time = df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i])
        
        # Bullish BOS: Close breaks above latest swing high
        valid_highs = [h for h in highs if h["index"] < i]
        if valid_highs:
            last_high = valid_highs[-1]
            if curr_close > last_high["price"]:
                prev_close = float(df["Close"].iloc[i-1])
                if prev_close <= last_high["price"]:
                    bos_events.append({
                        "type": "bos",
                        "direction": "bullish",
                        "time": curr_time,
                        "price": last_high["price"],
                        "index": i,
                        "broken_swing_time": last_high["time"],
                        "notes": "Close above prior swing high"
                    })
                    
        # Bearish BOS: Close breaks below latest swing low
        valid_lows = [l for l in lows if l["index"] < i]
        if valid_lows:
            last_low = valid_lows[-1]
            if curr_close < last_low["price"]:
                prev_close = float(df["Close"].iloc[i-1])
                if prev_close >= last_low["price"]:
                    bos_events.append({
                        "type": "bos",
                        "direction": "bearish",
                        "time": curr_time,
                        "price": last_low["price"],
                        "index": i,
                        "broken_swing_time": last_low["time"],
                        "notes": "Close below prior swing low"
                    })
                    
    return bos_events

def detect_change_of_character(df: pd.DataFrame, swing_points: list[dict]) -> list[dict]:
    choch_events = []
    highs = [s for s in swing_points if s["type"] == "swing_high"]
    lows = [s for s in swing_points if s["type"] == "swing_low"]
    
    for i in range(1, len(df)):
        curr_close = float(df["Close"].iloc[i])
        prev_close = float(df["Close"].iloc[i-1])
        curr_time = df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i])
        
        valid_highs = [h for h in highs if h["index"] < i]
        valid_lows = [l for l in lows if l["index"] < i]
        
        if len(valid_highs) >= 2 and len(valid_lows) >= 2:
            last_high = valid_highs[-1]
            prev_high = valid_highs[-2]
            last_low = valid_lows[-1]
            prev_low = valid_lows[-2]
            
            # Bearish CHOCh check:
            if last_high["price"] > prev_high["price"] and last_low["price"] > prev_low["price"]:
                if curr_close < last_low["price"] and prev_close >= last_low["price"]:
                    choch_events.append({
                        "type": "choch",
                        "direction": "bearish",
                        "time": curr_time,
                        "price": last_low["price"],
                        "index": i,
                        "notes": "Trend changes to bearish (breaks prior HL)"
                    })
                    
            # Bullish CHOCh check:
            if last_high["price"] < prev_high["price"] and last_low["price"] < prev_low["price"]:
                if curr_close > last_high["price"] and prev_close <= last_high["price"]:
                    choch_events.append({
                        "type": "choch",
                        "direction": "bullish",
                        "time": curr_time,
                        "price": last_high["price"],
                        "index": i,
                        "notes": "Trend changes to bullish (breaks prior LH)"
                    })
                    
    return choch_events

def detect_liquidity_sweep(df: pd.DataFrame, swing_points: list[dict]) -> list[dict]:
    sweeps = []
    highs = [s for s in swing_points if s["type"] == "swing_high"]
    lows = [s for s in swing_points if s["type"] == "swing_low"]
    
    for i in range(1, len(df)):
        curr_high = float(df["High"].iloc[i])
        curr_low = float(df["Low"].iloc[i])
        curr_close = float(df["Close"].iloc[i])
        curr_time = df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i])
        
        valid_highs = [h for h in highs if h["index"] < i]
        if valid_highs:
            last_high = valid_highs[-1]
            if curr_high > last_high["price"] and curr_close < last_high["price"]:
                sweeps.append({
                    "type": "liquidity_sweep",
                    "direction": "bearish",
                    "time": curr_time,
                    "price": last_high["price"],
                    "index": i,
                    "notes": "Swept prior high and closed below"
                })
                
        valid_lows = [l for l in lows if l["index"] < i]
        if valid_lows:
            last_low = valid_lows[-1]
            if curr_low < last_low["price"] and curr_close > last_low["price"]:
                sweeps.append({
                    "type": "liquidity_sweep",
                    "direction": "bullish",
                    "time": curr_time,
                    "price": last_low["price"],
                    "index": i,
                    "notes": "Swept prior low and closed above"
                })
                
    return sweeps

def detect_fair_value_gap(df: pd.DataFrame) -> list[dict]:
    fvgs = []
    if len(df) < 3:
        return fvgs
        
    for i in range(2, len(df)):
        c1 = df.iloc[i-2]
        c3 = df.iloc[i]
        
        time3 = df.index[i].isoformat() if hasattr(df.index[i], "isoformat") else str(df.index[i])
        
        # Bullish FVG: C1 High < C3 Low
        if c1["High"] < c3["Low"]:
            fvgs.append({
                "type": "fvg",
                "direction": "bullish",
                "time": time3,
                "index": i,
                "zone_top": float(c3["Low"]),
                "zone_bottom": float(c1["High"]),
                "price": float((c3["Low"] + c1["High"]) / 2),
                "notes": "Bullish FVG created"
            })
            
        # Bearish FVG: C1 Low > C3 High
        if c1["Low"] > c3["High"]:
            fvgs.append({
                "type": "fvg",
                "direction": "bearish",
                "time": time3,
                "index": i,
                "zone_top": float(c1["Low"]),
                "zone_bottom": float(c3["High"]),
                "price": float((c1["Low"] + c3["High"]) / 2),
                "notes": "Bearish FVG created"
            })
            
    return fvgs

def detect_order_block(df: pd.DataFrame) -> list[dict]:
    obs = []
    if len(df) < 15:
        return obs
        
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - df["Close"].shift()).abs()
    tr3 = (df["Low"] - df["Close"].shift()).abs()
    df_tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df_atr = df_tr.rolling(14).mean()
    
    for i in range(14, len(df)):
        curr_open = float(df["Open"].iloc[i])
        curr_close = float(df["Close"].iloc[i])
        prev_open = float(df["Open"].iloc[i-1])
        prev_close = float(df["Close"].iloc[i-1])
        atr = float(df_atr.iloc[i-1])
        
        if pd.isna(atr) or atr == 0:
            continue
            
        curr_body = curr_close - curr_open
        
        if curr_body > (1.5 * atr) and prev_close < prev_open:
            obs.append({
                "type": "order_block",
                "direction": "bullish",
                "time": df.index[i-1].isoformat() if hasattr(df.index[i-1], "isoformat") else str(df.index[i-1]),
                "index": i-1,
                "zone_top": float(df["High"].iloc[i-1]),
                "zone_bottom": float(df["Low"].iloc[i-1]),
                "price": float((df["High"].iloc[i-1] + df["Low"].iloc[i-1]) / 2),
                "notes": "Bearish candle prior to strong bullish impulse"
            })
            
        if curr_body < (-1.5 * atr) and prev_close > prev_open:
            obs.append({
                "type": "order_block",
                "direction": "bearish",
                "time": df.index[i-1].isoformat() if hasattr(df.index[i-1], "isoformat") else str(df.index[i-1]),
                "index": i-1,
                "zone_top": float(df["High"].iloc[i-1]),
                "zone_bottom": float(df["Low"].iloc[i-1]),
                "price": float((df["High"].iloc[i-1] + df["Low"].iloc[i-1]) / 2),
                "notes": "Bullish candle prior to strong bearish impulse"
            })
            
    return obs
