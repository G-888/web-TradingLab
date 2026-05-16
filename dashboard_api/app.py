from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dashboard_api.routes import overview, signals, backtests, alerts, performance, analysis, strategies, forward_tests, outlook, market, strategy_lab

import os

app = FastAPI(title="Dashboard API")

allowed_origins_str = os.getenv("DASHBOARD_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dashboard_api"}

# Include routers
app.include_router(overview.router, prefix="/api")
app.include_router(signals.router, prefix="/api/signals")
app.include_router(backtests.router, prefix="/api/backtests")
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(performance.router, prefix="/api/performance")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(strategies.router, prefix="/api/strategies")
app.include_router(forward_tests.router, prefix="/api/forward-tests")
app.include_router(outlook.router, prefix="/api/outlook")
app.include_router(market.router, prefix="/api/market")
app.include_router(strategy_lab.router, prefix="/api/strategy-lab")
