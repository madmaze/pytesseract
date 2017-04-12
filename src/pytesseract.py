#!/usr/bin/env python
'''
Python-tesseract. For more information: https://github.com/madmaze/pytesseract

'''

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd_default = 'tesseract'


try:
    import Image
except ImportError:
    from PIL import Image
import subprocess
import sys
import tempfile
import os
import shlex

__all__ = ['image_to_string']

def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False, config=None, quiet=True, tesseract_cmd=tesseract_cmd_default):
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
        
    if config:
        command += shlex.split(config)
    
    proc = subprocess.Popen(command,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    status = proc.wait()
    err_str = proc.stderr.read()
    if not quiet:
        out_str = proc.stdout.read()
        print out_str
        print >> sys.stderr, err_str
    return status, err_str

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

def image_to_string(image, lang=None, boxes=False, config=None, quiet=True, tesseract_cmd=tesseract_cmd_default):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Tesseract's result is
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
    if not boxes:
        output_file_name = '%s.txt' % output_file_name_base
    else:
        output_file_name = '%s.box' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             config=config,
                                             tesseract_cmd=tesseract_cmd,
                                             quiet=quiet
                                             )
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        f = open(output_file_name, 'rb')
        try:
            return f.read().decode('utf-8').strip()
        finally:
            f.close()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)

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
        sys.stderr.write('Usage: python pytesseract.py [-l language] input_file\n')
        exit(2)

if __name__ == '__main__':
    main()
