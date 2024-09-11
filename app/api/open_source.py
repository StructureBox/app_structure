from fastapi import APIRouter, HTTPException, Query
from services.steel import Steel
import logging

router = APIRouter()


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


@router.get("/get_section/excel/wc/{value}")
def get_wc_section_excel(
    H: float = Query(300, description="溝形鋼の高さ (mm)"),
    B: float = Query(100, description="溝形鋼の幅 (mm)"),
    tw: float = Query(8, description="ウェブの厚さ (mm)"),
    tf: float = Query(12, description="フランジの厚さ (mm)"),
    value: str = "A",
):
    """
    溝形鋼(WC)の寸法に基づいて、指定された値 (A, Ix, Iy, Zx, Zy, ix, iy, Cy) のみを出力します。

    Args:
        H (float): 溝形鋼の高さ (mm)
        B (float): 溝形鋼の幅 (mm)
        tw (float): ウェブの厚さ (mm)
        tf (float): フランジの厚さ (mm)
        value (str): 出力したい値 ("A", "Ix", "Iy", "Zx", "Zy", "ix", "iy", "Cy")

    Example:
        `/get_section/excel/wc/Ix?H=300&B=100&tw=8&tf=12` -> Ix（断面二次モーメントX軸）を返します。

    Returns:
        dict: 指定された値の結果を辞書形式で返します。
    """
    logging.debug(f"Getting WC-section data for size: WC-{H}*{B}*{tw}*{tf} and value: {value}")

    steel = Steel()

    shape, section, values = steel.get_section(f"WC-{H}*{B}*{tw}*{tf}")

    if values is None:
        logging.error(f"No WC-section data found for size: WC-{H}*{B}*{tw}*{tf}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するWC形鋼の断面が見つかりません")

    result = {}
    if value == "A":
        return values[0]
    elif value == "Ix":
        return values[1]
    elif value == "Iy":
        return values[2]
    elif value == "Zx":
        result["Zx"] = values[3]
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


@router.get("/get_section/excel/lc/{value}")
def get_lc_section_excel(
    H: float = Query(150, description="リップ形鋼の高さ (mm)"),
    B: float = Query(75, description="リップ形鋼の幅 (mm)"),
    C: float = Query(20, description="リップの長さ (mm)"),
    t: float = Query(2.5, description="板厚 (mm)"),
    value: str = "A",
):
    """
    リップ形鋼(LC)の寸法に基づいて、指定された値 (A, Ix, Iy, Zx, Zy, ix, iy, Cy) のみを出力します。

    Args:
        H (float): リップ形鋼の高さ (mm)
        B (float): リップ形鋼の幅 (mm)
        C (float): リップの長さ (mm)
        t (float): 板厚 (mm)
        value (str): 出力したい値 ("A", "Ix", "Iy", "Zx", "Zy", "ix", "iy", "Cy")

    Example:
        `/get_section/excel/lc/Zy?H=150&B=75&C=20&t=2.5` -> Zy（断面係数Y軸）を返します。

    Returns:
        dict: 指定された値の結果を辞書形式で返します。
    """
    logging.debug(f"Getting LC-section data for size: LC-{H}*{B}*{C}*{t} and value: {value}")

    steel = Steel()

    shape, section, values = steel.get_section(f"LC-{H}*{B}*{C}*{t}")

    if values is None:
        logging.error(f"No LC-section data found for size: LC-{H}*{B}*{C}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するLC形鋼の断面が見つかりません")

    result = {}
    if value == "A":
        return values[0]
    elif value == "Ix":
        return values[1]
    elif value == "Iy":
        return values[2]
    elif value == "Zx":
        result["Zx"] = values[3]
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


@router.get("/get_section/excel/box/{value}")
def get_box_section_excel(
    B: float = Query(150, description="正方形鋼管の幅 (mm)"),
    t: float = Query(6, description="板厚 (mm)"),
    value: str = "A",
):
    """
    正方形鋼管(BOX)の寸法に基づいて、指定された値 (A, Ix, Iy, Zx, Zy, ix, iy, Cy) のみを出力します。

    Args:
        B (float): 正方形鋼管の幅 (mm)
        t (float): 板厚 (mm)
        value (str): 出力したい値 ("A", "Ix", "Iy", "Zx", "Zy", "ix", "iy", "Cy")

    Example:
        `/get_section/excel/box/ix?B=150&t=6` -> ix（断面二次半径X軸）を返します。

    Returns:
        dict: 指定された値の結果を辞書形式で返します。
    """
    logging.debug(f"Getting BOX-section data for size: BOX-{B}*{t} and value: {value}")

    steel = Steel()

    shape, section, values = steel.get_section(f"BOX-{B}*{t}")

    if values is None:
        logging.error(f"No BOX-section data found for size: BOX-{B}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するBOX形鋼の断面が見つかりません")

    result = {}
    if value == "A":
        return values[0]
    elif value == "Ix":
        return values[1]
    elif value == "Iy":
        return values[2]
    elif value == "Zx":
        result["Zx"] = values[3]
    elif value == "Zy":
        return values[4]
    elif value == "ix":
        return values[5]
    elif value == "iy":
        return values[6]
    else:
        raise HTTPException(status_code=400, detail="無効な値が指定されました")

    return result


@router.get("/get_section/excel/pipe/{value}")
def get_pipe_section_excel(
    D: float = Query(150, description="円形鋼管の直径 (mm)"),
    t: float = Query(6, description="板厚 (mm)"),
    value: str = "A",
):
    """
    円形鋼管(PIPE)の寸法に基づいて、指定された値 (A, Ix, Iy, Zx, Zy, ix, iy, Cy) のみを出力します。

    Args:
        D (float): 円形鋼管の直径 (mm)
        t (float): 板厚 (mm)
        value (str): 出力したい値 ("A", "Ix", "Iy", "Zx", "Zy", "ix", "iy", "Cy")

    Example:
        `/get_section/excel/pipe/A?D=150&t=6` -> 断面積を返します。

    Returns:
        dict: 指定された値の結果を辞書形式で返します。
    """
    logging.debug(f"Getting PIPE-section data for size: PIPE-{D}*{t} and value: {value}")

    steel = Steel()

    shape, section, values = steel.get_section(f"PIPE-{D}*{t}")

    if values is None:
        logging.error(f"No PIPE-section data found for size: PIPE-{D}*{t}")
        raise HTTPException(status_code=404, detail="指定された寸法に一致するPIPE形鋼の断面が見つかりません")

    result = {}
    if value == "A":
        return values[0]
    elif value == "Ix":
        return values[1]
    elif value == "Iy":
        return values[2]
    elif value == "Zx":
        result["Zx"] = values[3]
    elif value == "Zy":
        return values[4]
    elif value == "ix":
        return values[5]
    elif value == "iy":
        return values[6]
    else:
        raise HTTPException(status_code=400, detail="無効な値が指定されました")

    return result
