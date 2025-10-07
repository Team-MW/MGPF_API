import easyocr

reader = easyocr.Reader(['fr'])

def extract_text(image_bytes):
    result = reader.readtext(image_bytes, detail=0)
    return " ".join(result).strip()
