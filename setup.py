import os
from sys import version_info, argv as sys_argv
from setuptools import setup, __version__ as tools_version


README_PATH = 'README.rst'
LONG_DESC = ''
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        LONG_DESC = readme.read()

INSTALL_REQUIRES = ['Pillow']
EXTRAS_REQUIRE = {}

if int(tools_version.split('.', 1)[0]) < 18:
    assert 'bdist_wheel' not in sys_argv, \
        'bdist_wheel requires setuptools >= 18'

    if version_info[:2] < (3, 4):
        INSTALL_REQUIRES.append('enum34')
else:
    EXTRAS_REQUIRE[':python_version<"3.4"'] = ['enum34']

setup(
    name='pytesseract',
    version='0.1.8',
    author='Samuel Hoffstaetter',
    author_email='samuel@hoffstaetter.com',
    maintainer='Matthias Lee',
    maintainer_email='pytesseract@madmaze.net',
    description=(
        "Python-tesseract is a python wrapper for Google's Tesseract-OCR"
    ),
    long_description=LONG_DESC,
    license='GPLv3',
    keywords='python-tesseract OCR Python',
    url='https://github.com/madmaze/python-tesseract',
    packages=['pytesseract'],
    package_dir={'pytesseract': 'src'},
    package_data={'pytesseract': ['*.png', '*.jpg']},
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points={
        'console_scripts': ['pytesseract = pytesseract.pytesseract:main']
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
