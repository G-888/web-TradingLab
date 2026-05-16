from fastapi import APIRouter, Depends
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_one, fetch_all, check_db_status
from dashboard_api.schemas import OverviewResponse

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    db_status = check_db_status()
    
    # Latest signal
    latest_signal = fetch_one("SELECT * FROM signal_history ORDER BY id DESC LIMIT 1")
    
    # Total signals
    total_signals_row = fetch_one("SELECT COUNT(*) as count FROM signal_history")
    total_signals = total_signals_row["count"] if total_signals_row else 0
    
    # Total backtest runs
    total_backtests_row = fetch_one("SELECT COUNT(*) as count FROM backtest_runs")
    total_backtest_runs = total_backtests_row["count"] if total_backtests_row else 0
    
    # Active alerts
    active_alerts_row = fetch_one("SELECT COUNT(*) as count FROM alerts WHERE triggered=0")
    active_alerts = active_alerts_row["count"] if active_alerts_row else 0
    
    # Latest backtest
    latest_backtest = fetch_one("SELECT * FROM backtest_runs ORDER BY id DESC LIMIT 1")
    
    # Latest performance snapshot
    latest_performance = fetch_one("SELECT * FROM performance_snapshots ORDER BY id DESC LIMIT 1")
    
    return OverviewResponse(
        latest_signal=latest_signal,
        total_signals=total_signals,
        total_backtest_runs=total_backtest_runs,
        active_alerts=active_alerts,
        latest_backtest=latest_backtest,
        latest_performance_snapshot=latest_performance,
        database_connected=db_status["database_connected"],
        database_path=db_status["database_path"]
    )
