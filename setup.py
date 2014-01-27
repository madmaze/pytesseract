import os
from setuptools import setup

# Function for reading readme.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pytesseract",
    version = "0.1",
    author = "Juarez Bochi",
    author_email="",
    description = ("Python-tesseract is a python wrapper for google's Tesseract-OCR "),
    license = "GPLv3",
    keywords = "python-tesseract OCR Python",
    url = "https://github.com/jbochi/python-tesseract",
    packages=['pytesseract'],
    long_description=read('README'),
    package_data = {'pytesseract': ['*.png','*.jpg']}
)
