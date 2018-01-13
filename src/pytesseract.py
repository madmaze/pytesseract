#!/usr/bin/env python

'''
Python-tesseract. For more information: https://github.com/madmaze/pytesseract

'''

try:
    import Image
except ImportError:
    from PIL import Image

import os
import sys
import subprocess
from pkgutil import find_loader
import tempfile
import shlex
from glob import iglob

numpy_installed = True if find_loader('numpy') is not None else False
if numpy_installed:
    from numpy import ndarray

__all__ = ['image_to_string', 'image_to_boxes', 'image_to_data']

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)


def get_errors(error_string):
    return u' '.join(
        line for line in error_string.decode('utf-8').splitlines()
    ).strip()


def cleanup(temp_name):
    ''' Tries to remove files by filename wildcard path. '''
    for filename in iglob(temp_name + '*'):
        try:
            os.remove(filename)
        except OSError:
            pass


def save_image(image, boxes=False):
    image = prepare(image)
    if len(image.getbands()) == 4:
        # In case we have 4 channels, lets discard the Alpha.
        image = image.convert('RGB')

    temp_name = tempfile.mktemp(prefix='tess_')
    input_file_name = temp_name + '.bmp'
    image.save(input_file_name)
    return temp_name

def run_tesseract(input_filename,
                  output_filename_base,
                  extension,
                  lang,
                  config='',
                  nice=0):
    command = []

    if not sys.platform.startswith('win32') and nice != 0:
        command += ('nice', '-n', str(nice))

    command += (tesseract_cmd, input_filename, output_filename_base)

    if lang is not None:
        command += ('-l', lang)

    command += shlex.split(config)

    if extension != 'box':
        command.append(extension)

    proc = subprocess.Popen(command, stderr=subprocess.PIPE)
    status_code, error_string = proc.wait(), proc.stderr.read()
    proc.stderr.close()

    if status_code:
        raise TesseractError(status, get_errors(error_string))

    return True

def prepare(image):
    if isinstance(image, Image.Image):
        return image

    if numpy_installed and isinstance(image, ndarray):
        return Image.fromarray(image)

    raise TypeError('Unsupported image object')

def run_and_get_output(image, extension, lang=None, config='', nice=None):
    temp_name = ''
    try:
        temp_name = save_image(image)
        input_filename = temp_name+'.bmp'
        output_filename_base = temp_name+'_out'
        run_tesseract(input_filename, output_filename_base, extension, lang, config, nice)
        with open(output_filename_base+'.'+extension, 'rb') as output_file:
            return output_file.read().decode('utf-8').strip()
    finally:
        cleanup(temp_name)

def file_to_dict(tsv, cell_delimiter, str_col_idx):
    rows = [row.split(cell_delimiter) for row in tsv.split('\n')]
    header = rows.pop(0)
    str_col_idx = str_col_idx if str_col_idx >= 0 else len(header) + str_col_idx
    return_obj = {}
    for i, head in enumerate(header):
        return_obj[head] = [int(row[i]) if i != str_col_idx else row[i] for row in rows]
    return return_obj

def image_to_string(image, lang=None, config='', nice=0, boxes=False):
    '''
    Returns the result of a Tesseract OCR run on the provided image to string
    '''
    if boxes:
        # Added for backwards compatibility
        print('\nWarning: Argument \'boxes\' is deprecated and will be removed'
        ' in future versions. Use function image_to_boxes instead.\n')
        return image_to_boxes(image, lang, config, nice)
    return run_and_get_output(image, 'txt', lang, config, nice)

def image_to_boxes(image, lang=None, config='', nice=0, dict_output=False):
    '''
    Returns string output containing recognized characters and their box boundaries
    '''
    config += 'batch.nochop makebox'
    if dict_output:
        box_header = 'char left bottom right top page\n'
        return file_to_dict(box_header+run_and_get_output(image, 'box', lang, config, nice), ' ', 0)
    
    return run_and_get_output(image, 'box', lang, config, nice)
    
def image_to_data(image, lang=None, config='', nice=0, dict_output=False):
    '''
    Returns string output containing box boundaries, confidences, and other information. 
    Requires Tesseract 3.05+
    '''
    if dict_output:
        return file_to_dict(run_and_get_output(image, 'tsv', lang, config, nice), '\t', -1)
    
    return run_and_get_output(image, 'tsv', lang, config, nice)
    

def main():
    if len(sys.argv) == 2:
        filename, lang = sys.argv[1], None
    elif len(sys.argv) == 4 and sys.argv[1] == '-l':
        filename, lang = sys.argv[3], sys.argv[2]
    else:
        sys.stderr.write('Usage: python pytesseract.py [-l lang] input_file\n')
        exit(2)

    try:
        print(image_to_string(Image.open(filename), lang=lang))
    except IOError:
        sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
        exit(1)


if __name__ == '__main__':
    main()
