from fastapi import APIRouter
from services.awareness import (
    get_incidence_age,
    get_incidence_state,
    get_mortality,
    get_sunprotection
)

router = APIRouter(prefix="/api/awareness", tags=["awareness"])


@router.get("/incidence-age")
def incidence_age():
    return get_incidence_age()


@router.get("/incidence-state")
def incidence_state():
    return get_incidence_state()


@router.get("/mortality")
def mortality():
    return get_mortality()


@router.get("/sunprotection")
def sunprotection():
    return get_sunprotection()