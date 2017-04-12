import os
from setuptools import setup


README_PATH = 'README.rst'
longDesc = ""
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        longDesc = readme.read()

setup(
    name = "pytesseract",
    version = "0.1.7",
    author = "Samuel Hoffstaetter",
    author_email="samuel@hoffstaetter.com",
    maintainer = "Matthias Lee",
    maintainer_email = "pytesseract@madmaze.net",
    description = ("Python-tesseract is a python wrapper for google's Tesseract-OCR"),
    long_description = longDesc,
    license = "GPLv3",
    keywords = "python-tesseract OCR Python",
    url = "https://github.com/madmaze/python-tesseract",
    packages=['pytesseract'],
    package_dir={'pytesseract': 'src'},
    package_data = {'pytesseract': ['*.png','*.jpg']},
    install_requires = ['Pillow'],
    entry_points = {'console_scripts': ['pytesseract = pytesseract.pytesseract:main']},
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
