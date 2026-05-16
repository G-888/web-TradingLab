from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from dashboard_api.auth import verify_api_key
from strategies.registry import (
    get_all_strategies,
    get_enabled_strategies,
    get_strategy,
    validate_strategy_id
)
from strategies.strategy_router import run_strategy
from dashboard_api.routes.market import get_market_candles

router = APIRouter(dependencies=[Depends(verify_api_key)])

class AnalyzeRequest(BaseModel):
    strategy_id: str
    symbol: str = "XAUUSD"
    timeframe: str = "H1"

@router.get("/")
def list_all_strategies():
    """Return all strategy registry items."""
    return get_all_strategies()

@router.get("/enabled")
def list_enabled_strategies():
    """Return strategies with status implemented or partial."""
    return get_enabled_strategies()

@router.get("/categories")
def list_categories():
    """Return available categories."""
    strats = get_all_strategies()
    categories = list(set([s["category"] for s in strats]))
    return sorted(categories)

@router.get("/roadmap")
def get_strategy_roadmap():
    """Return strategies grouped by status for the roadmap view."""
    strats = get_all_strategies()
    roadmap = {
        "implemented": [],
        "partial": [],
        "planned": [],
        "disabled": []
    }
    
    for s in strats:
        status = s.get("status", "planned")
        if status not in roadmap:
            roadmap[status] = []
            
        steps = s.get("implementation_steps", [])
        next_steps_count = len(steps)
        
        roadmap[status].append({
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "status": status,
            "complexity": s.get("complexity", "medium"),
            "risk_level": s.get("risk_level", "medium"),
            "readiness": s.get("readiness", {}),
            "next_steps_count": next_steps_count,
            "recommended_priority": s.get("recommended_priority", "medium")
        })
        
    return roadmap

@router.get("/summary")
def get_strategies_summary(
    symbol: str = Query("XAUUSD"),
    timeframe: str = Query("H1")
):
    """
    Return summary of all enabled strategies by running an analysis.
    """
    enabled = get_enabled_strategies()
    candles = get_market_candles(symbol, timeframe, limit=300)
    
    summary = []
    for s in enabled:
        try:
            res = run_strategy(s["id"], symbol, timeframe, candles)
            summary.append({
                "strategy_id": s["id"],
                "name": s["name"],
                "category": s["category"],
                "status": s["status"],
                "direction": res.get("direction", "NEUTRAL"),
                "confidence": res.get("confidence", 0),
                "reason": res.get("reason", "No reason provided.")
            })
        except Exception as e:
            summary.append({
                "strategy_id": s["id"],
                "name": s["name"],
                "category": s["category"],
                "status": s["status"],
                "direction": "NEUTRAL",
                "confidence": 0,
                "reason": f"Analysis failed: {str(e)}"
            })
            
    return summary

@router.get("/{strategy_id}")
def get_single_strategy(strategy_id: str):
    """Return single strategy definition."""
    if not validate_strategy_id(strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
    return get_strategy(strategy_id)

@router.get("/{strategy_id}/detail")
def get_strategy_detail(strategy_id: str):
    """Return full strategy metadata."""
    if not validate_strategy_id(strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
    return get_strategy(strategy_id)

@router.post("/analyze")
def analyze_strategy(req: AnalyzeRequest):
    """
    Run an analysis using a specific strategy.
    """
    if not validate_strategy_id(req.strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    candles = get_market_candles(req.symbol, req.timeframe, limit=300)
    result = run_strategy(req.strategy_id, req.symbol, req.timeframe, candles)
    return result

