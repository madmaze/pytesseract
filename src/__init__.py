try:
    from pytesseract import image_to_string
except ImportError:
    from pytesseract.pytesseract import image_to_string
