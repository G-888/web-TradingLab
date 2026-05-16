from fastapi import APIRouter, Depends
from typing import Optional
from dashboard_api.auth import verify_api_key
import datetime

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/market")
def get_market_outlook(symbol: str = "XAUUSD"):
    # This acts as a safe mock endpoint for market outlook.
    # In a real integration, this could pull AI text generation from GROQ_API_KEY.
    return {
        "symbol": symbol,
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "intraday_bias": "Bullish",
        "swing_bias": "Bullish",
        "regime": "Trending",
        "volatility": "High",
        "bullish_scenario": f"If {symbol} holds above the local support, expect a continuation towards the next major liquidity pool.",
        "bearish_scenario": f"A break below the immediate support could trigger a long squeeze, pushing {symbol} down to test the weekly open.",
        "neutral_scenario": "Price may chop between support and resistance as volume is currently low waiting for the New York session.",
        "key_levels": [
            {"price": 2045.50, "description": "Local Demand Zone"},
            {"price": 2060.00, "description": "Major Supply Zone"}
        ],
        "risk_notes": [
            "CPI data release today may cause massive slippage.",
            "Friday closing flows may alter the trend."
        ]
    }

@router.get("/news")
def get_news_outlook(symbol: str = "XAUUSD"):
    # Local placeholder for news integration.
    return {
        "symbol": symbol,
        "news_status": "placeholder",
        "high_impact_events": [
            {
                "time": "14:30",
                "currency": "USD",
                "event": "Core CPI m/m",
                "impact": "HIGH",
                "forecast": "0.3%",
                "previous": "0.4%"
            },
            {
                "time": "14:30",
                "currency": "USD",
                "event": "CPI m/m",
                "impact": "HIGH",
                "forecast": "0.4%",
                "previous": "0.4%"
            }
        ],
        "summary": "News integration is not fully configured yet. Showing mock placeholder data.",
        "risk_warning": "Avoid trading during high-impact news until calendar integration is enabled."
    }
