from fastapi import APIRouter, HTTPException
from models.steel_input_models import SteelGetSectionInput
from services.steel import Steel
import logging

# ルーターの作成
router = APIRouter()


@router.post("/get_section/")
def get_section(input_data: SteelGetSectionInput):
    logging.debug(f"Getting section data for size: {input_data.size}")
    steel = Steel()
    shape, section, values = steel.get_section(input_data.size)
    if values is None:
        logging.error(f"No section data found for size: {input_data.size}")
        raise HTTPException(status_code=404, detail="指定された部材寸法に一致する断面が見つかりません")
    return {
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
        "Cy": values[7] if len(values) > 7 else "N/A",  # Cyは一部の形状でのみ利用可能
    }
