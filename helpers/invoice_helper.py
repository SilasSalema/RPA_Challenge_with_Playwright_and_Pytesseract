import cv2
import pytesseract
import numpy as np
import re


def extrair_dados_invoice(image_path: str) -> dict:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--oem 3 --psm 4"
    text = pytesseract.image_to_string(thresh, lang="eng", config=config)

    # -----------------------------
    # 🔎 INVOICE NUMBER
    # -----------------------------
    invoice_number = re.search(r"Invoice\s*#?\s*(\d+)", text, re.IGNORECASE)

    # -----------------------------
    # 📅 INVOICE DATE
    # -----------------------------
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # 2019-06-03
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}",
    ]

    invoice_date = None
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            invoice_date = match
            break

    # -----------------------------
    # 🏢 COMPANY NAME
    # COMPANY NAME (robusto)
    # -----------------------------
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    company_keywords = ["LLC", "CORP"]

    company_name = None

    for line in lines[:10]:  # só analisa topo do documento
        upper_line = line.upper()

        if not any(char.isdigit() for char in line) and any(
            keyword in upper_line for keyword in company_keywords
        ):
            company_name = str(line).replace("INVOICE", "")
            break

    # -----------------------------
    # 💰 TOTAL DUE
    # -----------------------------
    total_patterns = [
        r"Balance\s*Due\:?\s*\$?\s*([\d,]+\.\d{2})",
        r"\bTotal\s*\$?\s*([\d,]+\.\d{2})",
    ]

    total_due = None
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            total_due = match
            break

    result = {
        "Invoice Number": invoice_number.group(1) if invoice_number else None,
        "Invoice Date": invoice_date.group(0) if invoice_date else None,
        "Company Name": company_name,
        "Total Due": total_due.group(1) if total_due else None,
    }

    return result
