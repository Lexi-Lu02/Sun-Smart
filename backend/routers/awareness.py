from fastapi import APIRouter
from services.awareness import (
    get_skin_cancer_data,
    get_heat_trend_data,
    get_awareness_content,
)

router = APIRouter(
    prefix="/api/awareness",
    tags=["awareness"]
)


@router.get("/skin-cancer")
def skin_cancer():
    return get_skin_cancer_data()


@router.get("/heat-trend")
def heat_trend():
    return get_heat_trend_data()


@router.get("/content")
def content():
    return get_awareness_content()