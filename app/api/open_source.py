from fastapi import APIRouter

router = APIRouter()


@router.post("/", tags=["tag"])
async def route_name():
    return {"message": "Hello World"}
