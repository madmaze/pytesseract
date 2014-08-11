import os
from setuptools import setup

setup(
    name = "pytesseract",
    version = "0.1.4",
    author = "Samuel Hoffstaetter",
    author_email="",
    maintainer = "Matthias Lee",
    maintainer_email = "pytesseract@madmaze.net",
    description = ("Python-tesseract is a python wrapper for google's Tesseract-OCR"),
    license = "GPLv3",
    keywords = "python-tesseract OCR Python",
    url = "https://github.com/madmaze/python-tesseract",
    packages=['pytesseract'],
    package_dir={'pytesseract': 'src'},
    package_data = {'pytesseract': ['*.png','*.jpg']}
)
