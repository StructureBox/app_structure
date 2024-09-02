# excel.py

from openpyxl import load_workbook
import pdfkit
import io


def edit_excel_template(template: io.BytesIO, **data) -> io.BytesIO:
    """
    受け取ったデータに基づいてエクセルテンプレートを編集する関数。
    """
    wb = load_workbook(template)
    ws = wb.active

    # データの編集（セルのアドレスは仮定です。実際のテンプレートに合わせて修正してください）
    ws["B1"] = data["architect_number"]
    ws["B2"] = data["architect_name"]
    ws["B3"] = data["office_number"]
    ws["B4"] = data["address"]
    ws["B5"] = data["phone_number"]
    ws["B6"] = data["client_name"]
    ws["B7"] = data["building_location"]
    ws["B8"] = data["building_name"]
    ws["B9"] = data["building_usage"]
    ws["B10"] = data["building_area"]
    ws["B11"] = data["total_area"]
    ws["B12"] = data["max_height"]
    ws["B13"] = data["eaves_height"]
    ws["B14"] = data["above_ground_floors"]
    ws["B15"] = data["underground_floors"]
    ws["B16"] = data["structure_type"]

    # 編集後のエクセルファイルをバイトストリームに保存
    edited_excel = io.BytesIO()
    wb.save(edited_excel)
    edited_excel.seek(0)

    return edited_excel


def convert_excel_to_pdf(excel_data: io.BytesIO) -> io.BytesIO:
    """
    エクセルデータをPDFに変換する関数。
    """
    pdf_bytes = io.BytesIO()
    pdfkit.from_file(excel_data, pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes
