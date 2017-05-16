Python Tesseract
================

Python-tesseract is an optical character recognition (OCR) tool for python.
That is, it will recognize and "read" the text embedded in images.

Python-tesseract is a wrapper for `Google's Tesseract-OCR Engine`_. It is also useful as a
stand-alone invocation script to tesseract, as it can read all image types
supported by the Python Imaging Library, including jpeg, png, gif, bmp, tiff,
and others, whereas tesseract-ocr by default only supports tiff and bmp.
Additionally, if used as a script, Python-tesseract will print the recognized
text in stead of writing it to a file. Support for confidence estimates and
bounding box data is planned for future releases.

.. _Google's Tesseract-OCR Engine: https://github.com/tesseract-ocr/tesseract

USAGE
-----
.. code-block:: python

    try:
        import Image
    except ImportError:
        from PIL import Image
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = '<full_path_to_your_tesseract_executable>'
    # Include the above line, if you don't have tesseract executable in your PATH
    # Example tesseract_cmd: 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'

    print(pytesseract.image_to_string(Image.open('test.png')))
    print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))

Add the following config, if you have tessdata error like: "Error opening data file..."

.. code-block:: python

    tessdata_dir_config = '--tessdata-dir "<replace_with_your_tessdata_dir_path>"'
    # Example config: '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
    # It's important to add double quotes around the dir path.

    pytesseract.image_to_string(image, lang='chi_sim', config=tessdata_dir_config)

INSTALLATION
------------

Prerequisites:

- Python-tesseract requires python 2.5+ or python 3.x
- You will need the Python Imaging Library (PIL) (or the Pillow fork).
  Under Debian/Ubuntu, this is the package **python-imaging** or **python3-imaging**.
- Install `Google Tesseract OCR <https://github.com/tesseract-ocr/tesseract>`_ 
  (additional info how to install the engine on Linux, Mac OSX and Windows).
  You must be able to invoke the tesseract command as *tesseract*. If this
  isn't the case, for example because tesseract isn't in your PATH, you will
  have to change the "tesseract_cmd" variable at the top of *tesseract.py*.
  Under Debian/Ubuntu you can use the package **tesseract-ocr**. 
  For Mac OS users. please install homebrew package **tesseract**.

| Installing via pip:
| See the `pytesseract package page <https://pypi.python.org/pypi/pytesseract>`_.

.. code-block:: bash

    $ (env)> pip install pytesseract


| Installing from source:

.. code-block:: bash

    $> git clone git@github.com:madmaze/pytesseract.git
    $ (env)> python setup.py install

LICENSE
-------
Python-tesseract is released under the GPL v3.

CONTRIBUTERS
------------
- Originally written by `Samuel Hoffstaetter <https://github.com/h>`_
- `Juarez Bochi <https://github.com/jbochi>`_
- `Matthias Lee <https://github.com/madmaze>`_
- `Lars Kistner <https://github.com/Sr4l>`_
