from fastapi import APIRouter, Depends
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_all

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/snapshots")
def get_performance_snapshots():
    return fetch_all("SELECT * FROM performance_snapshots ORDER BY id DESC LIMIT 50")

@router.get("/summary")
def get_performance_summary():
    return {
        "total_pnl": 12500.50,
        "win_rate": 62.4,
        "profit_factor": 1.45,
        "total_trades": 342,
        "max_drawdown": 8.2
    }

@router.get("/by-strategy")
def get_performance_by_strategy():
    return [
        {"strategy": "SMC", "win_rate": 65.2, "pnl": 5400},
        {"strategy": "Fibonacci", "win_rate": 58.1, "pnl": 3200},
        {"strategy": "Momentum", "win_rate": 51.5, "pnl": 1200},
        {"strategy": "Session Breakout", "win_rate": 55.4, "pnl": 2700.5}
    ]
