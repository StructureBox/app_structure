import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

from steel import Steel

# 環境変数をロード
load_dotenv()

# Supabaseの設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPIアプリの作成
app = FastAPI()

# CORSミドルウェアの動的設定
origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 環境変数またはデフォルト値を使用
    allow_credentials=True,
    allow_methods=["*"],  # 全てのHTTPメソッドを許可
    allow_headers=["*"],  # 全てのヘッダーを許可
)


class SteelGetSectionInput(BaseModel):
    size: str


# # 新しいユーザーのデータモデル
# class User(BaseModel):
#     name: str
#     age: int


# # データベースからデータを取得する例
# @app.get("/data")
# def get_data():
#     response = supabase.table("your_table_name").select("*").execute()
#     if response.status_code == 200:
#         return response.data
#     else:
#         return {"error": response.status_text}


# # データをSupabaseに挿入する例
# @app.post("/add_data")
# def add_data(name: str, age: int):
#     response = supabase.table("your_table_name").insert({"name": name, "age": age}).execute()
#     if response.status_code == 201:
#         return {"message": "Data inserted successfully"}
#     else:
#         return {"error": response.status_text}


@app.post("/get_section/")
def get_section(input_data: SteelGetSectionInput):
    steel = Steel()
    shape, section, values = steel.get_section(input_data.size)
    if values is None:
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


# ルートエンドポイント
@app.get("/")
def read_root():
    return RedirectResponse("./docs")
