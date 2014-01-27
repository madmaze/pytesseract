#!/usr/bin/env python
'''
Python-tesseract is an optical character recognition (OCR) tool for python.
That is, it will recognize and "read" the text embedded in images.

Python-tesseract is a wrapper for google's Tesseract-OCR
( http://code.google.com/p/tesseract-ocr/ ).  It is also useful as a
stand-alone invocation script to tesseract, as it can read all image types
supported by the Python Imaging Library, including jpeg, png, gif, bmp, tiff,
and others, whereas tesseract-ocr by default only supports tiff and bmp.
Additionally, if used as a script, Python-tesseract will print the recognized
text in stead of writing it to a file. Support for confidence estimates and
bounding box data is planned for future releases.


USAGE:
From the shell:
 $ ./tesseract.py test.png                  # prints recognized text in image
 $ ./tesseract.py -l fra test-european.jpg  # recognizes french text
In python:
 > import Image
 > from tesseract import image_to_string
 > print image_to_string(Image.open('test.png'))
 > print image_to_string(Image.open('test-european.jpg'), lang='fra')


INSTALLATION:
* Python-tesseract requires python 2.5 or later.
* You will need the Python Imaging Library (PIL).  Under Debian/Ubuntu, this is
  the package "python-imaging".
* Install google tesseract-ocr from http://code.google.com/p/tesseract-ocr/ .
  You must be able to invoke the tesseract command as "tesseract". If this
  isn't the case, for example because tesseract isn't in your PATH, you will
  have to change the "tesseract_cmd" variable at the top of 'tesseract.py'.


COPYRIGHT:
Python-tesseract is released under the GPL v3.
Copyright (c) Samuel Hoffstaetter, 2009
http://wiki.github.com/hoffstaetter/python-tesseract

'''

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

import Image
import StringIO
import subprocess
import sys
import os

__all__ = ['image_to_string']

def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False):
    '''
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`
    
    returns the exit status of tesseract, as well as tesseract's stderr output

    '''

    command = [tesseract_cmd, input_filename, output_filename_base]
    
    if lang is not None:
        command += ['-l', lang]

    if boxes:
        command += ['batch.nochop', 'makebox']
    
    proc = subprocess.Popen(command,
            stderr=subprocess.PIPE)
    return (proc.wait(), proc.stderr.read())

def cleanup(filename):
    ''' tries to remove the given filename. Ignores non-existent files '''
    try:
        os.remove(filename)
    except OSError:
        pass

def get_errors(error_string):
    '''
    returns all lines in the error_string that start with the string "error"

    '''

    lines = error_string.splitlines()
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if len(error_lines) > 0:
        return '\n'.join(error_lines)
    else:
        return error_string.strip()

def tempnam():
    ''' returns a temporary file-name '''

    # prevent os.tmpname from printing an error...
    stderr = sys.stderr
    try:
        sys.stderr = StringIO.StringIO()
        return os.tempnam(None, 'tess_')
    finally:
        sys.stderr = stderr

class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)

def image_to_string(image, lang=None, boxes=False):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.

    '''

    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    if not boxes:
        output_file_name = '%s.txt' % output_file_name_base
    else:
        output_file_name = '%s.box' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        f = file(output_file_name)
        try:
            return f.read().strip()
        finally:
            f.close()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            image = Image.open(filename)
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        print image_to_string(image)
    elif len(sys.argv) == 4 and sys.argv[1] == '-l':
        lang = sys.argv[2]
        filename = sys.argv[3]
        try:
            image = Image.open(filename)
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        print image_to_string(image, lang=lang)
    else:
        sys.stderr.write('Usage: python tesseract.py [-l language] input_file\n')
        exit(2)

