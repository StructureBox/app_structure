# app/api/excel.py

from fastapi import APIRouter, HTTPException, Body
from services.excel import process_excel_template
from models.excel_models import template_model_map

# ルーターの作成
router = APIRouter()

@router.post("/edit/{template_name}")
async def edit_excel_template_endpoint(
    template_name: str,
    input_data: dict = Body(
        ..., description="テンプレートを編集するために必要なデータ"
    ),
):
    """
    指定されたExcelテンプレートを編集し、ダウンロードリンクを返すエンドポイント。
    """
    # テンプレート名に基づいて入力モデルを取得
    model = template_model_map.get(template_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    # 入力データを検証
    try:
        validated_data = model(**input_data).dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")

    # テンプレートを処理してダウンロードリンクを取得
    result = process_excel_template(template_name, validated_data)

    return result
