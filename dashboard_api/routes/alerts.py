from fastapi import APIRouter, Depends
from dashboard_api.auth import verify_api_key
from dashboard_api.db import fetch_all

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("")
def get_alerts():
    # Return both active (triggered=0) and recently triggered (triggered=1)
    return fetch_all("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")
