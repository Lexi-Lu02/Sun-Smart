from fastapi import APIRouter, Query
from services.uv_service import fetch_uv_data

router = APIRouter(prefix="/api/uv", tags=["UV"])

@router.get("/current")
async def get_current_uv(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    skin_type: str = Query("type2", description="Fitzpatrick type1–type4"),
):
    """
    Main endpoint for US 1.1.
    Frontend sends GPS coords → returns UV index, burn time, alert message.
    """
    return await fetch_uv_data(lat, lon, skin_type)