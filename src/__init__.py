try:
    from pytesseract import image_to_string
    from pytesseract import image_to_data
    from pytesseract import image_to_boxes
except ImportError:
    from pytesseract.pytesseract import image_to_string
