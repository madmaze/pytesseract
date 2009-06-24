#!/usr/bin/env python
'''
Python-tesseract is a python wrapper to google tesseract-ocr
( http://code.google.com/p/tesseract-ocr/ ). Python-tesseract is also useful as
a supplemental script to tesseract, as it can read all image types supported by
PIL, including jpeg, png, gif, bmp, tiff, and others. Tesseract by default only
supports tiff and bmp.


INSTALLATION:
You will need to install tesseract as well as the Python Imaging Library (PIL).
Under Debian/Ubuntu, this is the package "python-imaging".
Python-tesseract requires python2.5 or later.


USAGE:
From the shell:
 $ ./tesseract.py image.jpeg         # prints the recognized text in the image
In python:
 > from tesseract import image_to_string
 > import Image
 > print image_to_string(Image('image.jpeg'))


COPYRIGHT:
Python-tesseract is released under the GPL v3.
Copyright (c) Samuel Hoffstaetter, 2009

'''

from __future__ import with_statement
import Image
import StringIO
import subprocess
import sys
import os

tesseract_cmd = 'tesseract'

__all__ = ['image_to_string']

def run_tesseract(input_filename, output_filename_base, lang=None):
    '''
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`
    
    returns the exit status of tesseract, as well as tesseract's stderr output

    '''

    command = [tesseract_cmd, input_filename, output_filename_base]
    if lang is not None:
        command += ['-l', lang]

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
    error_lines = (line for line in lines if line.find('Error') >= 0)
    return '\n'.join(error_lines)

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
    def __init__(status, message):
        self.status = status
        self.message = message

def image_to_string(image, lang=None):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.

    '''

    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    output_file_name = '%s.txt' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name, output_file_name_base, lang=lang)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        with file(output_file_name) as f:
            return f.read().strip()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python tesseract.py input_file\n')
        exit(1)
    else:
        image = Image.open(sys.argv[1])
        print image_to_string(image)

