from fastapi import APIRouter, Depends
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_all

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/runs")
def get_backtest_runs():
    return fetch_all("SELECT * FROM backtest_runs ORDER BY id DESC LIMIT 50")

@router.get("/{run_id}/trades")
def get_backtest_trades(run_id: int):
    return fetch_all("SELECT * FROM backtest_trades WHERE run_id = ? ORDER BY id ASC", (run_id,))

from pydantic import BaseModel

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    timeframe: str
    lookback: str
    initial_capital: float
    risk_per_trade: float

@router.post("/run")
def run_backtest(req: BacktestRequest):
    from strategies.strategy_router import run_backtest_adapter
    
    adapter_result = run_backtest_adapter(req.strategy, req.symbol, req.timeframe, req.lookback)
    
    if "error" in adapter_result:
        return {"error": adapter_result["error"]}
        
    return {
        "run_id": 999, # Mock ID for the legacy page visualization
        "summary": {
            "total_trades": adapter_result.get("total_trades", 0),
            "win_rate": adapter_result.get("win_rate", 0) * 100,
            "profit_factor": adapter_result.get("profit_factor", 0),
            "max_drawdown": adapter_result.get("max_drawdown", 0),
            "total_pnl": adapter_result.get("net_pnl", 0)
        },
        "trades": adapter_result.get("trades", []),
        "equity_curve": adapter_result.get("equity_curve", []),
        "drawdown_curve": adapter_result.get("drawdown_curve", []),
        "warnings": adapter_result.get("warnings", [])
    }
