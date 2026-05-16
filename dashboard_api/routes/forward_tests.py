from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_all, execute_query, fetch_one
import json
from strategies.registry import STRATEGY_REGISTRY

router = APIRouter()

class StartForwardTestRequest(BaseModel):
    symbol: str
    timeframe: str
    strategies: list[str]

@router.get("/sessions", dependencies=[Depends(verify_api_key)])
def get_sessions():
    return fetch_all("SELECT * FROM forward_test_sessions ORDER BY id DESC")

@router.post("/start", dependencies=[Depends(verify_api_key)])
def start_session(request: StartForwardTestRequest):
    if not request.strategies:
        raise HTTPException(status_code=400, detail="Must provide at least one strategy.")

    valid_strategies = []
    for s_id in request.strategies:
        s = STRATEGY_REGISTRY.get(s_id)
        if not s:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {s_id}")
        
        # Only allow implemented strategies that can forward test
        if s.get("status") != "implemented" or not s.get("testability", {}).get("can_forward_test", False):
            raise HTTPException(status_code=400, detail=f"Strategy {s_id} is not available for forward testing.")
        
        valid_strategies.append(s_id)

    if not valid_strategies:
        raise HTTPException(status_code=400, detail="No valid forward-testable strategies provided.")

    strategies_json = json.dumps(valid_strategies)
    
    existing = fetch_one(
        "SELECT id FROM forward_test_sessions WHERE symbol=? AND timeframe=? AND status IN ('ACTIVE', 'PENDING_MONITORING')",
        (request.symbol, request.timeframe)
    )
    if existing:
        raise HTTPException(status_code=400, detail="An active session already exists for this symbol and timeframe.")

    session_id = execute_query(
        "INSERT INTO forward_test_sessions (symbol, timeframe, strategies_json, status) VALUES (?, ?, ?, 'PENDING_MONITORING')",
        (request.symbol, request.timeframe, strategies_json)
    )
    
    return {"status": "started", "session_id": session_id, "message": "Session created. Pending monitoring."}

@router.post("/stop", dependencies=[Depends(verify_api_key)])
def stop_session(session_id: int):
    # Close open trades
    execute_query(
        "UPDATE forward_test_trades SET status='CLOSED', result='NEUTRAL', exit_time=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE session_id=? AND status='OPEN'",
        (session_id,)
    )
    # Stop session
    execute_query(
        "UPDATE forward_test_sessions SET status='STOPPED', stopped_at=CURRENT_TIMESTAMP WHERE id=?",
        (session_id,)
    )
    return {"status": "stopped", "session_id": session_id}

@router.get("/{session_id}/trades", dependencies=[Depends(verify_api_key)])
def get_session_trades(session_id: int):
    return fetch_all("SELECT * FROM forward_test_trades WHERE session_id=? ORDER BY id DESC", (session_id,))

@router.get("/report", dependencies=[Depends(verify_api_key)])
def get_report():
    trades = fetch_all("SELECT * FROM forward_test_trades")
    total = len(trades)
    open_trades = len([t for t in trades if t['status'] == 'OPEN'])
    closed_trades = len([t for t in trades if t['status'] == 'CLOSED'])
    wins = len([t for t in trades if t['result'] == 'WIN'])
    win_rate = (wins / closed_trades * 100) if closed_trades > 0 else 0
    
    pnl = sum([t['pnl'] for t in trades if t['pnl'] is not None])
    
    return {
        "total_virtual_trades": total,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "win_rate": round(win_rate, 2),
        "virtual_pnl": round(pnl, 2)
    }
