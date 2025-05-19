from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
def health_check():
    return JSONResponse(content={"status": "ok"})