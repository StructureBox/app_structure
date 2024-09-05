from fastapi import APIRouter, HTTPException, Body
from services.excel import get_excel_template, edit_excel_template
from models.excel_models import template_model_map
from services.supabase_utils import upload_to_supabase, generate_download_link
from datetime import datetime

# ルーターの作成
router = APIRouter()


@router.post("/edit/{template_name}")
async def process_excel(template_name: str, input_data: dict = Body(...)):
    model = template_model_map.get(template_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    validated_data = model(**input_data).dict()
    template = get_excel_template(template_name)
    edited_excel = edit_excel_template(template, template_name, validated_data)
    excel_file_name = f"{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    upload_to_supabase(excel_file_name, edited_excel)
    excel_download_url = generate_download_link(excel_file_name)

    return {"excel_download_url": excel_download_url}
