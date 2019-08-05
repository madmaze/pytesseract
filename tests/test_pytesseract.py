# encoding: utf-8

import os.path
from multiprocessing import Pool
from sys import platform, version_info

import pytest
from pytesseract import (
    Output,
    TSVNotSupported,
    get_tesseract_version,
    image_to_boxes,
    image_to_data,
    image_to_osd,
    image_to_pdf_or_hocr,
    image_to_string
)

from pytesseract.pytesseract import (
    numpy_installed,
    pandas_installed,
    prepare
)

if numpy_installed:
    import numpy as np

if pandas_installed:
    import pandas

try:
    from PIL import Image
except ImportError:
    import Image


IS_PYTHON_2 = version_info[:1] < (3, )
IS_PYTHON_3 = not IS_PYTHON_2

TESSERACT_VERSION = tuple(get_tesseract_version().version)  # to skip tests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

pytestmark = pytest.mark.pytesseract  # used marker for the module


@pytest.fixture(scope='session')
def test_file():
    return os.path.join(DATA_DIR, 'test.jpg')


@pytest.fixture(scope='session')
def test_file_european():
    return os.path.join(DATA_DIR, 'test-european.jpg')


@pytest.mark.parametrize(
    'test_file',
    [
        'test.jpg',
        'test.pgm',
        'test.png',
        'test.ppm',
        'test.tiff',
        'test.gif',
        # 'test.bmp',  # https://github.com/tesseract-ocr/tesseract/issues/2558
    ],
    ids=[
        'jpg',
        'pgm',
        'png',
        'ppm',
        'tiff',
        'gif',
        # 'bmp',
    ]
)
def test_image_to_string_with_image_type(test_file):
    # Don't perform assertion against full string in case the version
    # of tesseract installed doesn't catch it all. This test is testing
    # that pytesseract command line program is called correctly.
    if test_file.endswith('gif') and TESSERACT_VERSION[0] < 4:
        pytest.skip('skip gif test')
    test_file_path = os.path.join(DATA_DIR, test_file)
    assert 'The quick brown dog' in image_to_string(test_file_path, 'eng')


@pytest.mark.parametrize(
    'test_file', [
        os.path.join(DATA_DIR, 'test.jpg'),
        Image.open(os.path.join(DATA_DIR, 'test.jpg')),
    ],
    ids=['path_str', 'image_object']
)
def test_image_to_string_with_args_type(test_file):
    assert 'The quick brown dog' in image_to_string(test_file, 'eng')


@pytest.mark.lang_fra
def test_image_to_string_european(test_file_european):
    assert 'La volpe marrone' in image_to_string(test_file_european, 'fra')


@pytest.mark.skipif(
    platform.startswith('win32'),
    reason='used paths with `/` as separator'
)
def test_image_to_string_batch():
    batch_file = os.path.join(DATA_DIR, 'images.txt')
    assert 'The quick brown dog' in image_to_string(batch_file)


def test_image_to_string_multiprocessing():
    """Test parallel system calls."""
    test_files = ['test.jpg', 'test.pgm', 'test.png', 'test.ppm', 'test.tiff']
    test_files = [os.path.join(DATA_DIR, test_file) for test_file in test_files]
    p = Pool(2)
    results = p.map(image_to_string, test_files)
    for result in results:
        assert 'The quick brown dog' in result
    p.close()
    p.join()


def test_image_to_string_timeout(test_file):
    with pytest.raises(RuntimeError):
        image_to_string(test_file, timeout=0.000000001)


def test_image_to_boxes(test_file):
    result = image_to_boxes(test_file)
    assert isinstance(result, unicode if IS_PYTHON_2 else str)

    lines = result.strip().split('\n')
    assert len(lines) > 0

    assert lines[0].split(' ')[0] == 'T'  # T of word 'This'

    for line in lines:
        chars = line.split(' ')
        assert chars[1].isnumeric()  # left
        assert chars[2].isnumeric()  # top
        assert chars[3].isnumeric()  # width
        assert chars[4].isnumeric()  # height


def test_image_to_osd(test_file):
    result = image_to_osd(test_file)
    assert isinstance(result, unicode if IS_PYTHON_2 else str)
    for key in [
        'Page number', 'Orientation in degrees', 'Rotate',
        'Orientation confidence', 'Script', 'Script confidence'
    ]:
        assert key + ':' in result


@pytest.mark.parametrize('extension', ['pdf', 'hocr'])
def test_image_to_pdf_or_hocr(test_file, extension):
    result = image_to_pdf_or_hocr(test_file, extension=extension)

    if extension is 'pdf':
        if IS_PYTHON_2:
            assert isinstance(result, str)
            result = str(result).strip()
            assert result.startswith('%PDF')
            assert result.endswith('EOF')
        else:
            assert isinstance(result, bytes)

    if extension is 'hocr':
        assert isinstance(result, bytes)  # type
        result = result.decode('utf-8') if IS_PYTHON_2 else str(result, 'utf-8')
        result = str(result).strip()
        assert result.startswith('<?xml')
        assert result.endswith('</html>')


@pytest.mark.skipif(
    numpy_installed is False,
    reason='requires numpy'
)
def test_image_to_string_with_numpy_array(test_file):
    assert 'The quick brown dog' in image_to_string(
        np.array(Image.open(test_file)),
        'eng'
    )


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] >= (3, 5),
    reason='requires tesseract < 3.05'
)
def test_image_to_data__pandas_support(test_file):
    with pytest.raises(TSVNotSupported):
        image_to_data(test_file, output_type=Output.DATAFRAME)


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05'
)
@pytest.mark.skipif(
    pandas_installed is False,
    reason='requires pandas'
)
def test_image_to_data__pandas_output(test_file):
    """Test and compare the type and meta information of the result."""
    result = image_to_data(test_file, output_type=Output.DATAFRAME)
    assert isinstance(result, pandas.DataFrame)
    expected_columns = [
        'level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num',
        'left', 'top', 'width', 'height', 'conf', 'text'
    ]
    assert bool(set(result.columns).intersection(expected_columns))


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05'
)
@pytest.mark.parametrize(
    'output', [
        Output.BYTES,
        Output.DICT,
        Output.STRING,
    ],
    ids=[
        'bytes',
        'dict',
        'string',
    ]
)
def test_image_to_data_common_output(test_file, output):
    """Test and compare the type of the result."""
    result = image_to_data(test_file, output_type=output)
    expected_keys = [
        'level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num',
        'left', 'top', 'width', 'height', 'conf', 'text'
    ]

    if output is Output.BYTES:
        assert isinstance(result, bytes)

    elif output is Output.DICT:
        assert isinstance(result, dict)
        assert bool(set(result.keys()).intersection(expected_keys))

    elif output is Output.STRING:
        assert isinstance(result, unicode if IS_PYTHON_2 else str)
        for key in expected_keys:
            assert key in result


@pytest.mark.parametrize('obj', [1, 1., None], ids=['int', 'float', 'none'])
def test_wrong_prepare_type(obj):
    with pytest.raises(TypeError):
        prepare(obj)


@pytest.mark.parametrize(
    'path', [
        r'wrong_tesseract',
        r'',
        os.path.sep + r'wrong_tesseract',
        ],
    ids=[
        'executable_name',
        'empty_name',
        'absolute_path',
    ]
)
def test_wrong_tesseract_cmd(test_file, path):
    """Test wrong or missing tesseract command."""
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = path
    with pytest.raises(pytesseract.pytesseract.TesseractNotFoundError):
        pytesseract.pytesseract.image_to_string(test_file)
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'  # restore the def value
