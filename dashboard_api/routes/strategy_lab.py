from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import math

from dashboard_api.auth import verify_api_key
from strategies.registry import get_testable_strategies, get_strategy
from strategies.strategy_router import run_backtest_adapter, run_forward_test_adapter
from storage.database import (
    create_benchmark_run,
    update_benchmark_run_status,
    save_benchmark_result,
    get_benchmark_runs,
    get_benchmark_results,
    get_best_strategies_by_symbol
)

router = APIRouter(dependencies=[Depends(verify_api_key)])
logger = logging.getLogger(__name__)

class BacktestAllRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "H1"
    lookback: str = "90d"
    strategies: List[str] = ["all"]

class ForwardTestStartRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "H1"
    strategies: List[str] = ["all"]
    duration_days: int = 30

def _calculate_score(win_rate: float, profit_factor: float, max_drawdown: float, expectancy: float, total_trades: int) -> float:
    """
    Transparent scoring formula.
    score = (win_rate * 100) + (profit_factor * 10) - (abs(max_drawdown) * 2) + (expectancy * 50) + (min(total_trades, 100) * 0.1)
    """
    try:
        wr_w = float(win_rate) * 100
        pf_w = float(profit_factor) * 10
        dd_p = abs(float(max_drawdown)) * 2
        exp_w = float(expectancy) * 50
        tc_c = min(int(total_trades), 100) * 0.1
        score = wr_w + pf_w - dd_p + exp_w + tc_c
        return round(score, 2)
    except:
        return 0.0

@router.get("/testable")
def list_testable_strategies(type: str = Query("backtest")):
    """Return testable strategies based on the given type (backtest, forwardtest, analysis)."""
    return get_testable_strategies(type)

@router.post("/backtest-all")
def backtest_all_strategies(req: BacktestAllRequest):
    """
    Batch run backtests on multiple strategies and save results to benchmark database.
    """
    testable = get_testable_strategies("backtest")
    
    if req.strategies and req.strategies[0].lower() == "all":
        targets = testable
    else:
        targets = [s for s in testable if s["id"] in req.strategies]
        
    if not targets:
        return {"status": "error", "message": "No valid backtestable strategies found."}
        
    run_id = create_benchmark_run(
        run_type="backtest",
        symbol=req.symbol,
        timeframe=req.timeframe,
        strategies=[t["id"] for t in targets],
        lookback=req.lookback
    )
    
    results = []
    
    for s in targets:
        res = run_backtest_adapter(s["id"], req.symbol, req.timeframe, req.lookback)
        
        # If adapter returns error, skip
        if "error" in res:
            continue
            
        # Extract metrics
        total_trades = res.get("total_trades", 0)
        wins = res.get("wins", 0)
        losses = res.get("losses", 0)
        win_rate = res.get("win_rate", 0.0)
        profit_factor = res.get("profit_factor", 0.0)
        max_dd = res.get("max_drawdown", 0.0)
        net_pnl = res.get("net_pnl", 0.0)
        expectancy = res.get("expectancy", 0.0)
        sharpe = res.get("sharpe", 0.0)
        avg_rr = res.get("avg_rr", 0.0)
        
        score = _calculate_score(win_rate, profit_factor, max_dd, expectancy, total_trades)
        
        save_benchmark_result(
            run_id=run_id,
            strategy_id=s["id"],
            strategy_name=s["name"],
            symbol=req.symbol,
            timeframe=req.timeframe,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            net_pnl=net_pnl,
            expectancy=expectancy,
            sharpe=sharpe,
            avg_rr=avg_rr,
            score=score,
            result_json=res
        )
        
        results.append({
            "strategy_id": s["id"],
            "score": score
        })
        
    update_benchmark_run_status(run_id, "completed", f"Ran {len(results)} out of {len(targets)} strategies.")
    
    return {
        "status": "success",
        "run_id": run_id,
        "processed": len(results),
        "total": len(targets)
    }

@router.post("/forward-test/start")
def start_forward_test(req: ForwardTestStartRequest):
    """
    Start virtual/paper forward-test sessions.
    """
    testable = get_testable_strategies("forward_test")
    
    if req.strategies and req.strategies[0].lower() == "all":
        targets = testable
    else:
        targets = [s for s in testable if s["id"] in req.strategies]
        
    if not targets:
        return {"status": "error", "message": "No valid forward-testable strategies found."}
        
    run_id = create_benchmark_run(
        run_type="forward_test",
        symbol=req.symbol,
        timeframe=req.timeframe,
        strategies=[t["id"] for t in targets],
        lookback=f"{req.duration_days}d"
    )
    
    sessions = []
    for s in targets:
        res = run_forward_test_adapter(s["id"], req.symbol, req.timeframe, req.duration_days)
        if "error" not in res:
            sessions.append(s["id"])
            
    update_benchmark_run_status(run_id, "pending_monitoring", f"Configured {len(sessions)} paper sessions.")
    
    return {
        "status": "success",
        "run_id": run_id,
        "started_sessions": sessions,
        "warning": "PAPER TEST ONLY. Monitor loop must be active to record virtual trades."
    }

@router.get("/runs")
def list_benchmark_runs():
    """Return recent benchmark runs."""
    return get_benchmark_runs()

@router.get("/runs/{run_id}")
def get_benchmark_run_details(run_id: int):
    """Return detailed results for a specific benchmark run."""
    results = get_benchmark_results(run_id)
    return results

@router.get("/rankings")
def get_strategy_rankings(symbol: str = Query("XAUUSD"), timeframe: str = Query("H1")):
    """Return overall rankings for a specific symbol and timeframe."""
    return get_best_strategies_by_symbol(symbol, timeframe)

@router.get("/compare")
def compare_strategies(symbol: str = Query("XAUUSD"), timeframe: str = Query("H1")):
    """
    Compare top strategies and provide recommendations and warnings based on stored benchmarks.
    """
    top = get_best_strategies_by_symbol(symbol, timeframe, limit=50)
    
    if not top:
        return {
            "status": "empty",
            "message": "No benchmark results yet. Run a backtest to compare strategies."
        }
        
    best_by_score = sorted(top, key=lambda x: x["score"], reverse=True)[0]
    best_by_win_rate = sorted(top, key=lambda x: x["win_rate"], reverse=True)[0]
    best_by_profit_factor = sorted(top, key=lambda x: x["profit_factor"], reverse=True)[0]
    best_low_dd = sorted(top, key=lambda x: abs(x["max_drawdown"]))[0]
    
    # Filter for most consistent: high trades, solid win rate, decent pf
    consistent = [t for t in top if t["total_trades"] >= 20 and t["win_rate"] >= 0.45 and t["profit_factor"] >= 1.2]
    most_consistent = sorted(consistent, key=lambda x: x["score"], reverse=True)[0] if consistent else None
    
    warnings = []
    if best_by_score["total_trades"] < 20:
        warnings.append(f"Small sample size for top strategy ({best_by_score['total_trades']} trades).")
    if abs(best_by_score["max_drawdown"]) > 15.0:
        warnings.append(f"High historical drawdown on top strategy ({best_by_score['max_drawdown']}%).")
        
    # Check if there is a forward test confirmation (we look at the DB to see if any forward_test run exists for this strategy)
    # For now, we assume if we are looking at backtest scores, we warn if no forward test.
    warnings.append("No forward-test confirmation yet for the recommended strategies.")
        
    return {
        "status": "success",
        "best_by_score": best_by_score,
        "best_by_win_rate": best_by_win_rate,
        "best_by_profit_factor": best_by_profit_factor,
        "best_by_low_drawdown": best_low_dd,
        "most_consistent": most_consistent or best_by_score,
        "warnings": warnings
    }
