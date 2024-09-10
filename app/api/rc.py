from fastapi import APIRouter, HTTPException
from models.rc_input_models import RcGetSectionInput
from services.rcbeam import RCBeam
from services.rccolumn import RCColumn


# ルーターの作成
router = APIRouter()


@router.get("/")
async def route_name():
    return {"message": "Hello World"}
