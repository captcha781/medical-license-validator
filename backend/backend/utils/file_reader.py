import os
import mimetypes

from PIL import Image
import pytesseract
import fitz  # PyMuPDF

def read_file_safely(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type is None:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".pdf"]:
            return extract_text_from_pdf(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return extract_text_from_image(file_path)
        else:
            return extract_text_from_generic(file_path)

    if mime_type.startswith("text"):
        return extract_text_from_generic(file_path)
    elif mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif mime_type.startswith("image"):
        return extract_text_from_image(file_path)
    else:
        return extract_text_from_generic(file_path)

def extract_text_from_generic(file_path: str) -> str:
    with open(file_path, "rb") as f:
        raw = f.read()

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("latin1")
        except UnicodeDecodeError:
            return raw.decode("utf-8", errors="replace")

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)
