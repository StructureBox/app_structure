import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from supabase import create_client, Client
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# Supabaseの設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPIアプリの作成
app = FastAPI()

# # 新しいユーザーのデータモデル
# class User(BaseModel):
#     name: str
#     age: int


# データベースからデータを取得する例
@app.get("/data")
def get_data():
    response = supabase.table("your_table_name").select("*").execute()
    if response.status_code == 200:
        return response.data
    else:
        return {"error": response.status_text}


# データをSupabaseに挿入する例
@app.post("/add_data")
def add_data(name: str, age: int):
    response = supabase.table("your_table_name").insert({"name": name, "age": age}).execute()
    if response.status_code == 201:
        return {"message": "Data inserted successfully"}
    else:
        return {"error": response.status_text}


# ルートエンドポイント
@app.get("/")
def read_root():
    return RedirectResponse("./docs")
