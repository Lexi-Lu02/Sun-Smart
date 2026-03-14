from fastapi import APIRouter, HTTPException
from database import get_postcode

router = APIRouter(prefix="/api/postcode", tags=["Postcode"])


@router.get("/{postcode}")
def lookup_postcode(postcode: str):
    """
    Look up Australian postcode in database. Returns lat/lng and location label
    for use with UV API. Table postcodes_geo must be loaded (see data/reference/australian-postcodes.sql).
    """
    result = get_postcode(postcode)
    if result is None:
        raise HTTPException(status_code=404, detail="Postcode not found")
    return result
