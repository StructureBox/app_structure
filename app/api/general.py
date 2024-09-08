from fastapi import APIRouter, HTTPException, Body, Path
from typing import Type, Dict
from pydantic import BaseModel
from services.cmq import Cmq
from models.general_models import type_model_map

# ルーターの作成
router = APIRouter()

# CMQ処理用のインスタンス
cmq = Cmq()


@router.post("/cmq/{type_model}")
async def cmq_culc(
    type_model: str = Path(
        ..., description="使用する計算モデルの種類を指定。例: 'type_point', 'type_zone'など。"
    ),  # パスパラメータの説明を追加
    payload: Dict = Body(
        ..., description="計算に必要なデータを含む辞書形式。各モデルごとに異なるパラメータを含む。"
    ),  # ボディパラメータの説明を追加
):
    """
    CMQ計算を行うエンドポイント。<br /><br />
    詳しいドキュメントはこちらをご覧ください:  < [APIドキュメント](https://doc.structurebox.tech/products/api/culc_cmq) >
    <br />

    ### 概要:
    このエンドポイントは、与えられた `type_model` に基づいて、異なる計算モデルを適用し、
    CMQ（せん断力、曲げモーメントなど）の計算結果を返します。

    ### パスパラメータ:
    - **type_model**: 使用する計算モデルの種類。例: `type_point`, `type_zone`など。

    ### ボディパラメータ:
    - **payload**: 計算に必要なデータを含む辞書形式。各モデルに必要な入力パラメータを含みます。

    ### レスポンス:
    - 計算されたCMQ結果（せん断力、曲げモーメントなど）を返します。

    ### エラーレスポンス:
    - **400 Bad Request**: 無効な `type_model` もしくは入力データが不正な場合。
    """

    # type_modelに基づいて適切なPydanticモデルを選択
    if type_model not in type_model_map:
        raise HTTPException(status_code=400, detail="Invalid type_model provided")

    # 適切な入力モデルのクラスを取得
    model_class: Type[BaseModel] = type_model_map[type_model]

    try:
        # 受け取ったデータをモデルとして検証
        data = model_class(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    # type_modelごとに異なるCMQ計算を実行
    if type_model == "type_point":
        result = cmq.type_point(data.al, data.p, data.a)
    elif type_model == "type_zone":
        result = cmq.type_zone(data.al, data.a, data.b, data.w, data.awl, data.bwl)
    elif type_model == "type_rect_full":
        result = cmq.type_rect_full(data.al, data.w, data.wl)
    elif type_model == "type_rect_part":
        result = cmq.type_rect_part(data.al, data.a, data.b, data.w, data.wl)
    elif type_model == "type_tri_right_full":
        result = cmq.type_tri_right_full(data.al, data.w, data.wl)
    elif type_model == "type_tri_left_full":
        result = cmq.type_tri_left_full(data.al, data.w, data.wl)
    elif type_model == "type_tri_right_part":
        result = cmq.type_tri_right_part(data.al, data.a, data.b, data.w, data.wl)
    elif type_model == "type_tri_left_part":
        result = cmq.type_tri_left_part(data.al, data.a, data.b, data.w, data.wl)
    else:
        raise HTTPException(status_code=400, detail="Calculation type not supported")

    # 結果を整形して返却
    cmq_result = cmq.cmq_form(result, n=2)

    # 結果をレスポンスとして返却
    response = {
        "input_data": payload,
        "cmq_result": {
            "Ci": cmq_result[0],  # 部材の左端せん断力
            "Cj": cmq_result[1],  # 部材の右端せん断力
            "M0": cmq_result[2],  # 部材の中央における曲げモーメント
            "Qi": cmq_result[3],  # 左端におけるせん断力
            "Qj": cmq_result[4],  # 右端におけるせん断力
        },
    }
    return response
