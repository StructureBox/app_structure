from fastapi import APIRouter, HTTPException
from models.steel_input_models import SteelGetSectionInput
from services.steel import Steel
import logging

# ルーターの作成
router = APIRouter()

# この関数は指定された部材の寸法に基づいて断面情報を取得するAPIエンドポイントです。
# 入力データとして部材のサイズ（size）を受け取り、その部材の断面性能（A, Ix, Iy, Zx, Zyなど）を返します。
# 断面情報が見つからなかった場合、404エラーが返されます。
@router.post("/get_section/")
def get_section(input_data: SteelGetSectionInput):
    """
    指定された部材サイズに基づいて断面データを取得します。

    Args:
        input_data (SteelGetSectionInput): 部材の寸法を指定する入力データ。
    
    Returns:
        dict: 部材の断面性能を含む辞書を返します。データが見つからない場合は404エラーを返します。

    Raises:
        HTTPException: 指定されたサイズの部材が見つからない場合、404エラーが発生します。
    """
    logging.debug(f"Getting section data for size: {input_data.size}")
    
    # Steelクラスのインスタンスを作成
    steel = Steel()
    
    # 指定されたサイズに基づいて断面データを取得
    shape, section, values = steel.get_section(input_data.size)
    
    # データが見つからなかった場合、エラーメッセージをログに記録して404エラーを発生
    if values is None:
        logging.error(f"No section data found for size: {input_data.size}")
        raise HTTPException(status_code=404, detail="指定された部材寸法に一致する断面が見つかりません")
    
    # 見つかった場合は断面性能を辞書形式で返す
    return {
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
        "Cy": values[7] if len(values) > 7 else "N/A",  # 一部の形状でのみ利用可能なCy
    }
