#!/usr/bin/env python
# encoding: utf-8
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
```
 > try:
 >     import Image
 > except ImportError:
 >     from PIL import Image
 > import pytesseract
 > print(pytesseract.image_to_string(Image.open('test.png')))
 > print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))
```

INSTALLATION:

Prerequisites:
* Python-tesseract requires python 2.5 or later or python 3.
* You will need the Python Imaging Library (PIL).  Under Debian/Ubuntu, this is
  the package "python-imaging" or "python3-imaging" for python3.
* Install google tesseract-ocr from http://code.google.com/p/tesseract-ocr/ .
  You must be able to invoke the tesseract command as "tesseract". If this
  isn't the case, for example because tesseract isn't in your PATH, you will
  have to change the "tesseract_cmd" variable at the top of 'tesseract.py'.
  Under Debian/Ubuntu you can use the package "tesseract-ocr".
  
Installing via pip:   
See the [pytesseract package page](https://pypi.python.org/pypi/pytesseract)     
$> sudo pip install pytesseract   

Installing from source:   
$> git clone git@github.com:madmaze/pytesseract.git   
$> sudo python setup.py install    


LICENSE:
Python-tesseract is released under the GPL v3.

CONTRIBUTERS:
- Originally written by [Samuel Hoffstaetter](https://github.com/hoffstaetter) 
- [Juarez Bochi](https://github.com/jbochi)
- [Matthias Lee](https://github.com/madmaze)
- [Lars Kistner](https://github.com/Sr4l)

'''

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

try:
    import Image
except ImportError:
    from PIL import Image
import subprocess
import sys
import tempfile
import os
import shlex
import re
import collections
from lxml import etree

__all__ = ['image_to_string']

def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False,
                  word_boxes=False, config=None):
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
    if word_boxes:
        command += ['hocr']
        
    if config:
        command += shlex.split(config)
    
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
    tmpfile = tempfile.NamedTemporaryFile(prefix="tess_")
    return tmpfile.name

class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)

def image_to_string(image, lang=None, boxes=False, word_boxes=False,
                    config=None):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.
    
    also supports boxes and config.
    
    if boxes=True
        "batch.nochop makebox" gets added to the tesseract call
    if config is set, the config gets appended to the command.
        ex: config="-psm 6"

    '''

    if len(image.split()) == 4:
        # In case we have 4 channels, lets discard the Alpha.
        # Kind of a hack, should fix in the future some time.
        r, g, b, a = image.split()
        image = Image.merge("RGB", (r, g, b))
    
    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    if boxes:
        output_file_name = '%s.box' % output_file_name_base
    elif word_boxes:
        output_file_name = '%s.hocr' % output_file_name_base
    else:
        output_file_name = '%s.txt' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             word_boxes=word_boxes,
                                             config=config)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        f = open(output_file_name)
        try:
            content = f.read().strip()
            if word_boxes:
                parser = etree.XMLParser(target=OcrXmlTarget())
                return etree.XML(content, parser)
            else:
                return content
        finally:
            f.close()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)


WordBox = collections.namedtuple("WordBox", "word coords wconf")
class OcrXmlTarget(object):
    TITLE_RGX = re.compile(r"bbox (\d+) (\d+) (\d+) (\d+); x_wconf (\d+)")

    def __init__(self):
        self.lines = []
        self.current_line = None
        self.current_word = None
        self.current_word_info = None
        self.line_open = self.word_open = False

    def start(self, tag, attrib):
        if tag == '{http://www.w3.org/1999/xhtml}span':
            attrib = dict(attrib)
            cls = attrib['class']
            title = attrib.get('title', '')
            if cls == 'ocr_line':
                self.current_line = []
                self.line_open = True
            elif cls == 'ocrx_word':
                match = self.TITLE_RGX.match(title)
                if match:
                    self.current_word_info = tuple(map(int, match.groups()))
                self.current_word = ''
                self.word_open = True

    def end(self, tag):
        if tag == '{http://www.w3.org/1999/xhtml}span':
            if self.word_open:
                self.word_open = False
                self.current_line.append(
                    WordBox(self.current_word,
                            self.current_word_info[0:4],
                            self.current_word_info[4]))
                self.current_word_info = None
                self.current_word = None
            elif self.line_open:
                self.line_open = False
                self.lines.append(self.current_line)
                self.current_line = None

    def data(self, data):
        if self.word_open:
            self.current_word += data

    def comment(self, text):
        pass

    def close(self):
        lines = self.lines
        self.lines = []
        return lines


def test_word_boxes():
    res = image_to_string(Image.open('src/test-european.jpg'),
                          lang='deu', word_boxes=True)
    text = ' '.join([word_box.word for line in res for word_box in line])
    assert (u'The (quick) [brown] {fox} jumps! Over the S43,456.78 <lazy> #90'
            u' dog & duck/goose, as 12.5% of E-mail from aspammer@website.com'
            u' is spam. Der „schnelle” braune Fuchs springt über den faulen'
            u' Hund.' in text)
    assert res[0][0].coords == (105, 66, 178, 97)



def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            image = Image.open(filename)
            if len(image.split()) == 4:
                # In case we have 4 channels, lets discard the Alpha.
                # Kind of a hack, should fix in the future some time.
                r, g, b, a = image.split()
                image = Image.merge("RGB", (r, g, b))
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        print(image_to_string(image))
    elif len(sys.argv) == 4 and sys.argv[1] == '-l':
        lang = sys.argv[2]
        filename = sys.argv[3]
        try:
            image = Image.open(filename)
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        print(image_to_string(image, lang=lang))
    else:
        sys.stderr.write('Usage: python tesseract.py [-l language] input_file\n')
        exit(2)

if __name__ == '__main__':
    main()
