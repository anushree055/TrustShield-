from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import io

def extract_text(image_bytes: bytes) -> dict:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        gray = ImageOps.grayscale(image)
        gray = ImageEnhance.Contrast(gray).enhance(1.5)
        text = pytesseract.image_to_string(gray, config="--psm 6").strip()
        return {"text": text, "characters": len(text), "success": bool(text)}
    except Exception as exc:
        return {"text": "", "characters": 0, "success": False, "error": str(exc)}
