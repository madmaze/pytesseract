try:
    from pytesseract import image_to_string
    from pytesseract import image_to_data
    from pytesseract import image_to_boxes
    from pytesseract import Output
except ImportError:
    from pytesseract.pytesseract import image_to_string
    from pytesseract.pytesseract import image_to_data
    from pytesseract.pytesseract import image_to_boxes
    from pytesseract.pytesseract import Output
