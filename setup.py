import os

from setuptools import setup

README_PATH = 'README.rst'
LONG_DESC = ''
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        LONG_DESC = readme.read()

INSTALL_REQUIRES = ['Pillow']
PACKAGE_NAME = 'pytesseract'
PACKAGE_DIR = 'src'

setup(
    name=PACKAGE_NAME,
    version='0.3.2',
    author='Samuel Hoffstaetter',
    author_email='samuel@hoffstaetter.com',
    maintainer='Matthias Lee',
    maintainer_email='pytesseract@madmaze.net',
    description=(
        "Python-tesseract is a python wrapper for Google's Tesseract-OCR"
    ),
    long_description=LONG_DESC,
    license='Apache License 2.0',
    keywords='python-tesseract OCR Python',
    url='https://github.com/madmaze/pytesseract',
    packages=[PACKAGE_NAME],
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': ['{0} = {0}.{0}:main'.format(PACKAGE_NAME)],
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
