import os.path
from sys import version_info as PYTHON_VERSION
from multiprocessing import Pool

import pytest

from pytesseract.pytesseract import get_tesseract_version, image_to_data, \
    image_to_string, prepare
from pytesseract.pytesseract import Output, TSVNotSupported

try:
    import pandas
except ImportError:
    pandas = None


TESSERACT_VERSION = tuple(get_tesseract_version().version)  # to skip tests
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


pytestmark = pytest.mark.pytesseract  # used marker for the module


@pytest.fixture(scope='session')
def test_file():
    return os.path.join(DATA_DIR, 'test.png')


@pytest.mark.parametrize('test_file', [
    # os.path.join(DATA_DIR, 'test.bmp'),
    os.path.join(DATA_DIR, 'test.gif'),
    os.path.join(DATA_DIR, 'test.jpeg'),
    os.path.join(DATA_DIR, 'test.pgm'),
    os.path.join(DATA_DIR, 'test.png'),
    os.path.join(DATA_DIR, 'test.ppm'),
    os.path.join(DATA_DIR, 'test.tiff'),
], ids=[
    # 'bmp',
    'gif',
    'jpeg',
    'pgm',
    'png',
    'ppm',
    'tiff',
])
def test_image_formats(test_file):
    # Don't perform assertion against full string in case the version
    # of tesseract installed doesn't catch it all. This test is testing
    # that pytesseract command line program is called correctly.
    assert 'The quick brown dog' in image_to_string(test_file, 'eng')


def test_multiprocessing(test_file):
    """Test parallel system calls."""
    test_files = [
        os.path.join(DATA_DIR, 'test.gif'),
        os.path.join(DATA_DIR, 'test.jpeg'),
        os.path.join(DATA_DIR, 'test.pgm'),
        os.path.join(DATA_DIR, 'test.png'),
        os.path.join(DATA_DIR, 'test.ppm'),
        os.path.join(DATA_DIR, 'test.tiff'),
    ]
    p = Pool(2)
    results = p.map(image_to_string, test_files)
    for result in results:
        assert 'The quick brown dog' in result
    p.close()
    p.join()


@pytest.mark.lang_fra
def test_european_image():
    test_file = os.path.join(DATA_DIR, 'test-european.jpg')
    assert 'La volpe marrone' in image_to_string(test_file, 'fra')


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] >= (3, 5),
    reason='requires tesseract < 3.05'
)
def test_pandas_support(test_file):
    with pytest.raises(TSVNotSupported):
        image_to_data(test_file, output_type=Output.DATAFRAME)


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05'
)
@pytest.mark.skipif(
    pandas is None,
    reason='requires pandas'
)
def test_pandas_output(test_file):
    """Test and compare the type and meta information of the result."""
    result = image_to_data(test_file, output_type=Output.DATAFRAME)
    assert isinstance(result, pandas.DataFrame)
    expected_columns = ['level', 'page_num', 'block_num', 'par_num',
                        'line_num', 'word_num', 'left', 'top', 'width',
                        'height', 'conf', 'text']
    assert bool(set(result.columns).intersection(expected_columns))


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05'
)
@pytest.mark.parametrize('output', [
    Output.BYTES,
    Output.DICT,
    Output.STRING,
], ids=[
    'bytes',
    'dict',
    'string',
])
def test_common_output(test_file, output):
    """Test and compare the type of the result."""
    result = image_to_data(test_file, output_type=output)
    if output is Output.BYTES:
        assert isinstance(result, bytes)
    elif output is Output.DICT:
        assert isinstance(result, dict)
    elif output is Output.STRING:
        if PYTHON_VERSION[:1] < (3, ):
            assert isinstance(result, unicode)
        else:
            assert isinstance(result, str)


@pytest.mark.parametrize('obj', [1, 1., None], ids=['int', 'float', 'none'])
def test_invalid_type_in_prepare(obj):
    with pytest.raises(TypeError):
        prepare(obj)


@pytest.mark.parametrize('path', [
    r'invalid_tesseract',
    r'',
    os.path.sep + r'invalid_tesseract',
], ids=[
    'executable_name',
    'empty_name',
    'absolute_path',
])
def test_wrong_cmd(test_file, path):  # This must be the last test!
    """Test invalid or missing tesseract command."""
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = path
    with pytest.raises(pytesseract.pytesseract.TesseractNotFoundError):
        pytesseract.pytesseract.image_to_string(test_file)
