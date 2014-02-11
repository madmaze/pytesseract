Python-tesseract is an optical character recognition (OCR) tool for python.
That is, it will recognize and "read" the text embedded in images.

Python-tesseract is a wrapper for google's Tesseract-OCR
( http://code.google.com/p/tesseract-ocr/ ).  It is also useful as a
stand-alone invocation script to tesseract, as it can read all image types
supported by the Python Imaging Library, including jpeg, png, gif, bmp, tiff,
and others, wheras tesseract-ocr by default only supports tiff and bmp.
Additionally, if used as a script, Python-tesseract will print the recognized
text in stead of writing it to a file. Support for confidence estimates and
bounding box data is planned for future releases.


USAGE:
```
From the shell:
 $ ./pytesseract.py test.png                  # prints recognized text in image
 $ ./pytesseract.py -l fra test-european.jpg  # recognizes french text
In python:
 > import Image
 > from pytesseract import image_to_string
 > print image_to_string(Image.open('test.png'))
 > print image_to_string(Image.open('test-european.jpg'), lang='fra')
```

Specifying a config file:

```
 > import Image
 > from pytesseract import image_to_string
 > print image_to_string(Image.open('test.png'), config="digits")

```

INSTALLATION:
* Python-tesseract requires python 2.5 or later.
* You will need the Python Imaging Library (PIL).  Under Debian/Ubuntu, this is
  the package "python-imaging".
* Install google tesseract-ocr from http://code.google.com/p/tesseract-ocr/ .
  You must be able to invoke the tesseract command as "tesseract". If this
  isn't the case, for example because tesseract isn't in your PATH, you will
  have to change the "tesseract_cmd" variable at the top of 'tesseract.py'.


LICENSE:
Python-tesseract is released under the GPL v3.

CONTRIBUTERS:
- Originally written by [Samuel Hoffstaetter](https://github.com/hoffstaetter) 
- [Juarez Bochi](https://github.com/jbochi)
- [Matthias Lee](https://github.com/madmaze)

