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

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'
img_mode = 'RGB'


class Output:
    STRING = "string"
    BYTES = "bytes"
    DICT = "dict"


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
    for filename in iglob(temp_name + '*' if temp_name else temp_name):
        try:
            os.remove(filename)
        except OSError:
            pass


def prepare(image):
    if isinstance(image, Image.Image):
        return image

    if numpy_installed and isinstance(image, ndarray):
        return Image.fromarray(image)

    raise TypeError('Unsupported image object')


def save_image(image):
    image = prepare(image)

    img_extension = image.format
    if image.format not in {'JPEG', 'PNG', 'TIFF', 'BMP', 'GIF'}:
        img_extension = 'PNG'

    if not image.mode.startswith(img_mode):
        image = image.convert(img_mode)

    if 'A' in image.getbands():
        # discard and replace the alpha channel with white background
        background = Image.new(img_mode, image.size, (255, 255, 255))
        background.paste(image, (0, 0), image)
        image = background

    temp_name = tempfile.mktemp(prefix='tess_')
    input_file_name = temp_name + os.extsep + img_extension
    image.save(input_file_name, format=img_extension, **image.info)
    return temp_name, img_extension


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
        raise TesseractError(status_code, get_errors(error_string))

    return True


def run_and_get_output(image,
                       extension,
                       lang=None,
                       config='',
                       nice=None,
                       return_bytes=False):
    temp_name = ''
    img_extension = ''
    try:
        temp_name, img_extension = save_image(image)
        kwargs = {
            'input_filename': temp_name + os.extsep + img_extension,
            'output_filename_base': temp_name + '_out',
            'extension': extension,
            'lang': lang,
            'config': config,
            'nice': nice
        }

        run_tesseract(**kwargs)
        filename = kwargs['output_filename_base'] + os.extsep + extension
        with open(filename, 'rb') as output_file:
            if return_bytes:
                return output_file.read()
            return output_file.read().decode('utf-8').strip()
    finally:
        cleanup(temp_name)


def file_to_dict(tsv, cell_delimiter, str_col_idx):
    result = {}
    rows = [row.split(cell_delimiter) for row in tsv.split('\n')]
    if not rows:
        return result

    header = rows.pop(0)
    if rows and len(rows[-1]) < len(header):
        # Fixes bug that occurs when last text string in TSV is null, and
        # last row is missing a final cell in TSV file
        rows[-1].append('')

    if str_col_idx < 0:
        str_col_idx += len(header)

    for i, head in enumerate(header):
        result[head] = [
            int(row[i]) if i != str_col_idx else row[i] for row in rows
        ]

    return result


def image_to_string(image,
                    lang=None,
                    config='',
                    nice=0,
                    boxes=False,
                    output_type=Output.STRING):
    '''
    Returns the result of a Tesseract OCR run on the provided image to string
    '''
    if boxes:
        # Added for backwards compatibility
        print('\nWarning: Argument \'boxes\' is deprecated and will be removed'
              ' in future versions. Use function image_to_boxes instead.\n')
        return image_to_boxes(image, lang, config, nice, output_type)

    if output_type == Output.DICT:
        return {'text': run_and_get_output(image, 'txt', lang, config, nice)}
    elif output_type == Output.BYTES:
        return run_and_get_output(image, 'txt', lang, config, nice, True)

    return run_and_get_output(image, 'txt', lang, config, nice)


def image_to_boxes(image,
                   lang=None,
                   config='',
                   nice=0,
                   output_type=Output.STRING):
    '''
    Returns string containing recognized characters and their box boundaries
    '''
    config += ' batch.nochop makebox'

    if output_type == Output.DICT:
        box_header = 'char left bottom right top page\n'
        return file_to_dict(
            box_header + run_and_get_output(
                image, 'box', lang, config, nice), ' ', 0)
    elif output_type == Output.BYTES:
        return run_and_get_output(image, 'box', lang, config, nice, True)

    return run_and_get_output(image, 'box', lang, config, nice)


def image_to_data(image,
                  lang=None,
                  config='',
                  nice=0,
                  output_type=Output.STRING):
    '''
    Returns string containing box boundaries, confidences,
    and other information. Requires Tesseract 3.05+
    '''
    if output_type == Output.DICT:
        return file_to_dict(
            run_and_get_output(image, 'tsv', lang, config, nice), '\t', -1)
    elif output_type == Output.BYTES:
        return run_and_get_output(image, 'tsv', lang, config, nice, True)

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
