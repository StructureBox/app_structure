from fastapi import APIRouter, HTTPException, Body
from services.excel import get_excel_template, edit_excel_template
from models.excel_models import template_model_map
from services.supabase_utils import upload_to_supabase, generate_download_link
from datetime import datetime

# ルーターの作成
router = APIRouter()


@router.post("/dxf/{template_name}")
async def process_excel(template_name: str):
    """
    指定されたdxfテンプレートのダウンロードリンクを返します。

    - `template_name`: dxfテンプレートの名前

    詳しいドキュメントはこちらをご覧ください:  < [APIドキュメント](https://doc.structurebox.tech/products/sheet/edit_excel_template) >
    """
    # テンプレート名に基づいて入力モデルを取得
    model = template_model_map.get(template_name)
    if not model:
        # テンプレートが見つからない場合のエラーハンドリング
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    # 入力データを検証し、辞書形式に変換
    validated_data = model(**input_data).dict()

    # Excelテンプレートを取得
    template = get_excel_template(template_name)

    # テンプレートを編集してデータを埋め込む
    edited_excel = edit_excel_template(template, template_name, validated_data)

    # ファイル名に現在の日時を付加してSupabaseにアップロード
    excel_file_name = f"{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    upload_to_supabase(excel_file_name, edited_excel)

    # アップロードされたファイルのダウンロードリンクを生成
    excel_download_url = generate_download_link(excel_file_name)

    # ダウンロードリンクを返却
    return {"excel_download_url": excel_download_url}