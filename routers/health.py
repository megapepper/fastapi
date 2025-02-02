from fastapi import APIRouter


router = APIRouter()
@router.get("/health", status_code=200)
def check_health():
    return "health OK"