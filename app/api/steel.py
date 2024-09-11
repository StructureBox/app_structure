from fastapi import APIRouter, HTTPException, Query
from models.steel_input_models import (
    SteelPostSectionInput,
    HSectionInput,
    WCSectionInput,
    LCSectionInput,
    BOXSectionInput,
    PIPESectionInput,
)
from services.steel import Steel
import logging

# ルーターの作成
router = APIRouter()


# この関数は指定された部材の寸法に基づいて断面情報を取得するAPIエンドポイントです。
# 入力データとして部材のサイズ（size）を受け取り、その部材の断面性能（A, Ix, Iy, Zx, Zyなど）を返します。
# 断面情報が見つからなかった場合、404エラーが返されます。
@router.post("/post_section/")
def post_section(input_data: SteelPostSectionInput):
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
    shape, section, values = steel.post_section(input_data.size)

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


# H形鋼の断面性能を取得するエンドポイント
@router.post("/post_section/h")
def post_h_section(input_data: HSectionInput):
    """
    H形鋼の寸法に基づいて断面データを取得します。

    Args:
        input_data (HSectionInput): H形鋼の寸法を指定する入力データ。

    Returns:
        dict: H形鋼の断面性能を含む辞書を返します。データが見つからなかった場合は404エラーを返します。
    """
    logging.debug(f"Getting H-section data for size: {input_data}")

    steel = Steel()

    # 指定されたサイズに基づいて断面データを取得
    shape, section, values = steel.post_section(
        f"H-{input_data.H}*{input_data.B}*{input_data.tw}*{input_data.tf}"
    )

    if values is None:
        logging.error(f"No H-section data found for size: {input_data}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するH形鋼の断面が見つかりません")

    return {
        "形状": f"H-{input_data.H}*{input_data.B}*{input_data.tw}*{input_data.tf}",
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
    }


# 溝形鋼(WC)の断面性能を取得するエンドポイント
@router.post("/post_section/wc")
def post_wc_section(input_data: WCSectionInput):
    """
    溝形鋼(WC)の寸法に基づいて断面データを取得します。

    Args:
        input_data (WCSectionInput): 溝形鋼の寸法を指定する入力データ。

    Returns:
        dict: 溝形鋼の断面性能を含む辞書を返します。データが見つからなかった場合は404エラーを返します。
    """
    logging.debug(f"Getting WC-section data for size: {input_data}")

    steel = Steel()

    shape, section, values = steel.post_section(
        f"WC-{input_data.H}*{input_data.B}*{input_data.tw}*{input_data.tf}"
    )

    if values is None:
        logging.error(f"No WC-section data found for size: {input_data}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するWC形鋼の断面が見つかりません")

    return {
        "形状": f"WC-{input_data.H}*{input_data.B}*{input_data.tw}*{input_data.tf}",
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
        "Cy": values[7],  # Cy（Y軸方向のせん断中心）
    }


# リップ形鋼(LC)の断面性能を取得するエンドポイント
@router.post("/post_section/lc")
def post_lc_section(input_data: LCSectionInput):
    """
    リップ形鋼(LC)の寸法に基づいて断面データを取得します。

    Args:
        input_data (LCSectionInput): リップ形鋼の寸法を指定する入力データ。

    Returns:
        dict: リップ形鋼の断面性能を含む辞書を返します。データが見つからなかった場合は404エラーを返します。
    """
    logging.debug(f"Getting LC-section data for size: {input_data}")

    steel = Steel()

    shape, section, values = steel.post_section(
        f"LC-{input_data.H}*{input_data.B}*{input_data.C}*{input_data.t}"
    )

    if values is None:
        logging.error(f"No LC-section data found for size: {input_data}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するLC形鋼の断面が見つかりません")

    return {
        "形状": f"LC-{input_data.H}*{input_data.B}*{input_data.C}*{input_data.t}",
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
        "Cy": values[7],  # Cy
    }


# 正方形鋼管(BOX)の断面性能を取得するエンドポイント
@router.post("/post_section/box")
def post_box_section(input_data: BOXSectionInput):
    """
    正方形鋼管(BOX)の寸法に基づいて断面データを取得します。

    Args:
        input_data (BOXSectionInput): 正方形鋼管の寸法を指定する入力データ。

    Returns:
        dict: 正方形鋼管の断面性能を含む辞書を返します。データが見つからなかった場合は404エラーを返します。
    """
    logging.debug(f"Getting BOX-section data for size: {input_data}")

    steel = Steel()

    shape, section, values = steel.post_section(f"BOX-{input_data.B}*{input_data.t}")

    if values is None:
        logging.error(f"No BOX-section data found for size: {input_data}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するBOX形鋼の断面が見つかりません")

    return {
        "形状": f"BOX-{input_data.B}*{input_data.t}",
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
    }


# 円形鋼管(PIPE)の断面性能を取得するエンドポイント
@router.post("/post_section/pipe")
def post_pipe_section(input_data: PIPESectionInput):
    """
    円形鋼管(PIPE)の寸法に基づいて断面データを取得します。

    Args:
        input_data (PIPESectionInput): 円形鋼管の寸法を指定する入力データ。

    Returns:
        dict: 円形鋼管の断面性能を含む辞書を返します。データが見つからなかった場合は404エラーを返します。
    """
    logging.debug(f"Getting PIPE-section data for size: {input_data}")

    steel = Steel()

    shape, section, values = steel.post_section(f"PIPE-{input_data.D}*{input_data.t}")

    if values is None:
        logging.error(f"No PIPE-section data found for size: {input_data}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するPIPE形鋼の断面が見つかりません")

    return {
        "形状": f"PIPE-{input_data.D}*{input_data.t}",
        "A": values[0],  # 断面積
        "Ix": values[1],  # 断面二次モーメント（X軸）
        "Iy": values[2],  # 断面二次モーメント（Y軸）
        "Zx": values[3],  # 断面係数（X軸）
        "Zy": values[4],  # 断面係数（Y軸）
        "ix": values[5],  # 断面二次半径（X軸）
        "iy": values[6],  # 断面二次半径（Y軸）
    }


# H形鋼の断面性能をクエリパラメータで取得する
@router.get("/get_section/h")
def get_h_section(
    H: float = Query(300, description="H形鋼の高さ (mm)"),
    B: float = Query(150, description="H形鋼の幅 (mm)"),
    tw: float = Query(6.5, description="H形鋼のウェブの厚さ (mm)"),
    tf: float = Query(9, description="H形鋼のフランジの厚さ (mm)"),
):
    """
    H形鋼の寸法をクエリパラメータで指定して断面性能を取得します。

    クエリパラメータ:
    - `H`: 高さ（mm）
    - `B`: 幅（mm）
    - `tw`: ウェブの厚さ（mm）
    - `tf`: フランジの厚さ（mm）

    例:
    `steel/get_section/h?H=300&B=150&tw=6.5&tf=9`
    """
    logging.debug(f"Getting H-section data for size: H-{H}*{B}*{tw}*{tf}")

    steel = Steel()

    shape, section, values = steel.post_section(f"H-{H}*{B}*{tw}*{tf}")

    if values is None:
        logging.error(f"No H-section data found for size: H-{H}*{B}*{tw}*{tf}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するH形鋼の断面が見つかりません")

    return {
        "形状": f"H-{H}*{B}*{tw}*{tf}",
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
    }


# 溝形鋼(WC)の断面性能をクエリパラメータで取得する
@router.get("/get_section/wc")
def get_wc_section(
    H: float = Query(300, description="溝形鋼の高さ (mm)"),
    B: float = Query(100, description="溝形鋼の幅 (mm)"),
    tw: float = Query(8, description="溝形鋼のウェブの厚さ (mm)"),
    tf: float = Query(12, description="溝形鋼のフランジの厚さ (mm)"),
):
    """
    溝形鋼(WC)の寸法をクエリパラメータで指定して断面性能を取得します。

    クエリパラメータ:
    - `H`: 高さ（mm）
    - `B`: 幅（mm）
    - `tw`: ウェブの厚さ（mm）
    - `tf`: フランジの厚さ（mm）

    例:
    `steel/get_section/wc?H=300&B=100&tw=8&tf=12`
    """
    logging.debug(f"Getting WC-section data for size: WC-{H}*{B}*{tw}*{tf}")

    steel = Steel()

    shape, section, values = steel.post_section(f"WC-{H}*{B}*{tw}*{tf}")

    if values is None:
        logging.error(f"No WC-section data found for size: WC-{H}*{B}*{tw}*{tf}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するWC形鋼の断面が見つかりません")

    return {
        "形状": f"WC-{H}*{B}*{tw}*{tf}",
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
    }


# リップ形鋼(LC)の断面性能をクエリパラメータで取得する
@router.get("/get_section/lc")
def get_lc_section(
    H: float = Query(150, description="リップ形鋼の高さ (mm)"),
    B: float = Query(75, description="リップ形鋼の幅 (mm)"),
    C: float = Query(20, description="リップの長さ (mm)"),
    t: float = Query(2.5, description="板厚 (mm)"),
):
    """
    リップ形鋼(LC)の寸法をクエリパラメータで指定して断面性能を取得します。

    クエリパラメータ:
    - `H`: 高さ（mm）
    - `B`: 幅（mm）
    - `C`: リップの長さ（mm）
    - `t`: 厚さ（mm）

    例:
    `steel/get_section/lc?H=150&B=75&C=20&t=2.5`
    """
    logging.debug(f"Getting LC-section data for size: LC-{H}*{B}*{C}*{t}")

    steel = Steel()

    shape, section, values = steel.post_section(f"LC-{H}*{B}*{C}*{t}")

    if values is None:
        logging.error(f"No LC-section data found for size: LC-{H}*{B}*{C}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するLC形鋼の断面が見つかりません")

    return {
        "形状": f"LC-{H}*{B}*{C}*{t}",
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
    }


# 正方形鋼管(BOX)の断面性能をクエリパラメータで取得する
@router.get("/get_section/box")
def get_box_section(
    B: float = Query(150, description="正方形鋼管の一辺の長さ (mm)"),
    t: float = Query(6, description="板厚 (mm)"),
):
    """
    正方形鋼管(BOX)の寸法をクエリパラメータで指定して断面性能を取得します。

    クエリパラメータ:
    - `B`: 一辺の長さ（mm）
    - `t`: 厚さ（mm）

    例:
    `steel/get_section/box?B=150&t=6`
    """
    logging.debug(f"Getting BOX-section data for size: BOX-{B}*{t}")

    steel = Steel()

    shape, section, values = steel.post_section(f"BOX-{B}*{t}")

    if values is None:
        logging.error(f"No BOX-section data found for size: BOX-{B}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するBOX形鋼の断面が見つかりません")

    return {
        "形状": f"BOX-{B}*{t}",
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
    }


# 円形鋼管(PIPE)の断面性能をクエリパラメータで取得する
@router.get("/get_section/pipe")
def get_pipe_section(
    D: float = Query(150, description="円形鋼管の外径 (mm)"), t: float = Query(6, description="板厚 (mm)")
):
    """
    円形鋼管(PIPE)の寸法をクエリパラメータで指定して断面性能を取得します。

    クエリパラメータ:
    - `D`: 外径（mm）
    - `t`: 厚さ（mm）

    例:
    `steel/get_section/pipe?D=150&t=6`
    """
    logging.debug(f"Getting PIPE-section data for size: PIPE-{D}*{t}")

    steel = Steel()

    shape, section, values = steel.post_section(f"PIPE-{D}*{t}")

    if values is None:
        logging.error(f"No PIPE-section data found for size: PIPE-{D}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するPIPE形鋼の断面が見つかりません")

    return {
        "形状": f"PIPE-{D}*{t}",
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
    }


# H形鋼の断面性能をパスパラメータで取得する
@router.get("/get_section/excel/h/{value}")
def get_h_section_excel(
    H: float = Query(300, description="H形鋼の高さ (mm)"),
    B: float = Query(150, description="H形鋼の幅 (mm)"),
    tw: float = Query(6.5, description="ウェブの厚さ (mm)"),
    tf: float = Query(9, description="フランジの厚さ (mm)"),
    value: str = "A",
):
    """
    H形鋼の寸法に基づいて、指定された値 (A, Ix, Iy, Zx, Zy, ix, iy, Cy) のみを出力します。

    Args:
        H (float): H形鋼の高さ (mm)
        B (float): H形鋼の幅 (mm)
        tw (float): ウェブの厚さ (mm)
        tf (float): フランジの厚さ (mm)
        value (str): 出力したい値 ("A", "Ix", "Iy", "Zx", "Zy", "ix", "iy", "Cy")

    Example:
        `steel/get_section/excel/h/A?H=300&B=150&tw=6.5&tf=9` -> 断面積を返します。

    Returns:
        dict: 指定された値の結果を辞書形式で返します。
    """
    logging.debug(f"Getting H-section data for size: H-{H}*{B}*{tw}*{tf} and value: {value}")

    steel = Steel()

    shape, section, values = steel.get_section(f"H-{H}*{B}*{tw}*{tf}")

    if values is None:
        logging.error(f"No H-section data found for size: H-{H}*{B}*{tw}*{tf}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するH形鋼の断面が見つかりません")

    result = {}
    if value == "A":
        return values[0]
    elif value == "Ix":
        return values[1]
    elif value == "Iy":
        return values[2]
    elif value == "Zx":
        return values[3]
    elif value == "Zy":
        return values[4]
    elif value == "ix":
        return values[5]
    elif value == "iy":
        return values[6]
    elif value == "Cy" and len(values) > 7:
        return values[7]
    else:
        raise HTTPException(status_code=400, detail="無効な値が指定されました")

    return result
