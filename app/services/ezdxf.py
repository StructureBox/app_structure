# import os
# import ezdxf
# import matplotlib.pyplot as plt
# from ezdxf.addons.drawing import RenderContext, Frontend
# from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
# from pydantic import BaseModel
# from fastapi import HTTPException

# # from typing import Optional
# from supabase import create_client, Client
# from dotenv import load_dotenv

# # 環境変数をロード
# load_dotenv()

# # Supabaseの設定
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# # Supabaseクライアントの作成
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# class DXFEditRequest(BaseModel):
#     file_id: str
#     # 必要に応じて他の編集に関するパラメータを追加


# async def create_dxf():
#     # 新規のdxfを作成してバージョンを定義する
#     doc = ezdxf.new("R2010")
#     # モデルスペースを変数に定義する
#     msp = doc.modelspace()
#     # モデルスペースに線を挿入
#     msp.add_line((0, 0), (1000000, 0))
#     # dxfを現在のディレクトリに保存
#     doc.saveas("dxf/図面1.dxf")

#     fig = plt.figure()
#     ax = fig.add_axes([0, 0, 1, 1])
#     ctx = RenderContext(doc)
#     out = MatplotlibBackend(ax)
#     Frontend(ctx, out).draw_layout(msp, finalize=True)
#     print(fig.show())


# async def edit_dxf(data: DXFEditRequest):
#     try:
#         # ローカルのDXFファイルを読み込む
#         local_dxf_path = "./dxf/test.dxf"

#         if not os.path.exists(local_dxf_path):
#             raise HTTPException(status_code=404, detail="Local DXF file not found")

#         # DXFファイルの読み込み
#         doc = ezdxf.readfile(local_dxf_path)

#         # DXFデータの編集 (例: 図形を追加)
#         msp = doc.modelspace()
#         msp.add_circle((0, 0), radius=5000)

#         # 編集済みのDXFデータを直接ローカルに保存
#         edited_dxf_path = f"./dxf/edited_{data.file_id}.dxf"
#         doc.saveas(edited_dxf_path)

#         # ファイルの存在を確認
#         if not os.path.exists(edited_dxf_path):
#             raise HTTPException(status_code=500, detail="Failed to save edited DXF file locally")

#         # Supabaseに保存
#         with open(edited_dxf_path, "rb") as edited_file:
#             upload_response = supabase.storage.from_("dxf-files").upload(
#                 f"edited_{data.file_id}.dxf", edited_file
#             )

#         # アップロードの成功確認
#         if upload_response.get("error") is not None:
#             raise HTTPException(status_code=500, detail="Failed to upload edited DXF file")

#         # ダウンロードリンクを取得
#         download_url = supabase.storage.from_("dxf-files").get_public_url(f"edited_{data.file_id}.dxf")

#         return {"download_url": download_url}

#     except Exception as e:
#         # エラーハンドリング
#         raise HTTPException(status_code=500, detail=str(e))
