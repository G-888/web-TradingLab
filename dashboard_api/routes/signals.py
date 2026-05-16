from fastapi import APIRouter, Depends, Query
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_all

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/latest")
def get_latest_signals():
    return fetch_all("SELECT * FROM signal_history ORDER BY id DESC LIMIT 10")

@router.get("/history")
def get_signal_history(
    symbol: str = Query("XAUUSD"),
    timeframe: str = Query(None),
    limit: int = Query(100)
):
    # The existing schema might not have symbol, so we fetch all and let the UI handle or 
    # we just fetch with timeframe if provided.
    
    query = "SELECT * FROM signal_history"
    params = []
    
    if timeframe:
        query += " WHERE timeframe = ?"
        params.append(timeframe)
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    results = fetch_all(query, tuple(params))
    
    # If symbol is missing in DB (it is initially missing from schema), we inject it
    for row in results:
        if "symbol" not in row:
            row["symbol"] = "XAUUSD" # Default injected symbol
            
    # Filter by symbol explicitly since sqlite might not have the column
    results = [r for r in results if r.get("symbol") == symbol]
            
    return results
