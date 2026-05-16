from pydantic import BaseModel
from typing import Optional, List, Any

class OverviewResponse(BaseModel):
    latest_signal: Optional[dict] = None
    total_signals: int = 0
    total_backtest_runs: int = 0
    active_alerts: int = 0
    latest_backtest: Optional[dict] = None
    latest_performance_snapshot: Optional[dict] = None
    database_connected: bool = False
    database_path: str = ""

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "dashboard_api"
