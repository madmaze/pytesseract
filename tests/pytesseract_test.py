from glob import iglob
from multiprocessing import Pool
from os import getcwd
from os import path
from os import sep
from sys import platform
from sys import version_info
from tempfile import gettempdir
from unittest import mock

import pytest

from pytesseract import ALTONotSupported
from pytesseract import get_languages
from pytesseract import get_tesseract_version
from pytesseract import image_to_alto_xml
from pytesseract import image_to_boxes
from pytesseract import image_to_data
from pytesseract import image_to_osd
from pytesseract import image_to_pdf_or_hocr
from pytesseract import image_to_string
from pytesseract import Output
from pytesseract import TesseractNotFoundError
from pytesseract import TSVNotSupported
from pytesseract.pytesseract import file_to_dict
from pytesseract.pytesseract import numpy_installed
from pytesseract.pytesseract import pandas_installed
from pytesseract.pytesseract import prepare

if numpy_installed:
    import numpy as np

if pandas_installed:
    import pandas

try:
    from PIL import Image
except ImportError:
    import Image


IS_PYTHON_2 = version_info[:1] < (3,)
IS_PYTHON_3 = not IS_PYTHON_2

TESSERACT_VERSION = tuple(get_tesseract_version().release)  # to skip tests

TESTS_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(TESTS_DIR, 'data')
TESSDATA_DIR = path.join(TESTS_DIR, 'tessdata')
TEST_JPEG = path.join(DATA_DIR, 'test.jpg')

pytestmark = pytest.mark.pytesseract  # used marker for the module
string_type = unicode if IS_PYTHON_2 else str  # noqa: 821


@pytest.fixture(scope='session')
def test_file():
    return TEST_JPEG


@pytest.fixture(scope='session')
def test_invalid_file():
    return TEST_JPEG + 'invalid'


@pytest.fixture(scope='session')
def test_file_european():
    return path.join(DATA_DIR, 'test-european.jpg')


@pytest.fixture(scope='session')
def test_file_small():
    return path.join(DATA_DIR, 'test-small.jpg')


@pytest.mark.parametrize(
    'test_file',
    [
        'test.jpg',
        'test.jpeg2000',
        'test.pgm',
        'test.png',
        'test.ppm',
        'test.tiff',
        'test.gif',
        'test.webp',
        # 'test.bmp',  # https://github.com/tesseract-ocr/tesseract/issues/2558
    ],
    ids=[
        'jpg',
        'jpeg2000',
        'pgm',
        'png',
        'ppm',
        'tiff',
        'gif',
        'webp',
        # 'bmp',
    ],
)
def test_image_to_string_with_image_type(test_file):
    # Don't perform assertion against full string in case the version
    # of tesseract installed doesn't catch it all. This test is testing
    # that pytesseract command line program is called correctly.
    if test_file.endswith('gif') and TESSERACT_VERSION[0] < 4:
        pytest.skip('skip gif test')
    test_file_path = path.join(DATA_DIR, test_file)
    assert 'The quick brown dog' in image_to_string(test_file_path, 'eng')


@pytest.mark.parametrize(
    'test_file',
    [TEST_JPEG, Image.open(TEST_JPEG)],
    ids=['path_str', 'image_object'],
)
def test_image_to_string_with_args_type(test_file):
    assert 'The quick brown dog' in image_to_string(test_file, 'eng')

    # Test cleanup of temporary files
    for _ in iglob(gettempdir() + sep + 'tess_*'):
        assert False, 'Failed to cleanup temporary files'


@pytest.mark.skipif(numpy_installed is False, reason='requires numpy')
def test_image_to_string_with_numpy_array(test_file):
    assert 'The quick brown dog' in image_to_string(
        np.array(Image.open(test_file)),
        'eng',
    )


@pytest.mark.lang_fra
def test_image_to_string_european(test_file_european):
    assert 'La volpe marrone' in image_to_string(test_file_european, 'fra')


@pytest.mark.skipif(
    platform.startswith('win32'),
    reason='used paths with `/` as separator',
)
def test_image_to_string_batch():
    batch_file = path.join(DATA_DIR, 'images.txt')
    assert 'The quick brown dog' in image_to_string(batch_file)


def test_image_to_string_multiprocessing():
    """Test parallel system calls."""
    test_files = [
        'test.jpg',
        'test.pgm',
        'test.png',
        'test.ppm',
        'test.tiff',
        'test.webp',
    ]
    test_files = [path.join(DATA_DIR, test_file) for test_file in test_files]
    p = Pool(2)
    results = p.map(image_to_string, test_files)
    for result in results:
        assert 'The quick brown dog' in result
    p.close()
    p.join()


def test_image_to_string_timeout(test_file):
    with pytest.raises(RuntimeError):
        image_to_string(test_file, timeout=0.000000001)


def test_la_image_to_string():
    filepath = path.join(DATA_DIR, 'test_la.png')
    img = Image.open(filepath)
    assert 'This is test message' == image_to_string(img).strip()


def test_image_to_boxes(test_file):
    result = image_to_boxes(test_file)
    assert isinstance(result, string_type)

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
    assert isinstance(result, string_type)
    for key in [
        'Page number',
        'Orientation in degrees',
        'Rotate',
        'Orientation confidence',
        'Script',
        'Script confidence',
    ]:
        assert key + ':' in result


@pytest.mark.parametrize('extension', ['pdf', 'hocr'])
def test_image_to_pdf_or_hocr(test_file, extension):
    result = image_to_pdf_or_hocr(test_file, extension=extension)

    if extension == 'pdf':
        if IS_PYTHON_2:
            assert isinstance(result, str)
            result = str(result).strip()
            assert result.startswith('%PDF')
            assert result.endswith('EOF')
        else:
            assert isinstance(result, bytes)

    if extension == 'hocr':
        assert isinstance(result, bytes)  # type
        result = (
            result.decode('utf-8') if IS_PYTHON_2 else str(result, 'utf-8')
        )
        result = str(result).strip()
        assert result.startswith('<?xml')
        assert result.endswith('</html>')


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (4, 1),
    reason='requires tesseract >= 4.1',
)
def test_image_to_alto_xml(test_file):
    result = image_to_alto_xml(test_file)
    assert isinstance(result, bytes)
    result = result.decode('utf-8') if IS_PYTHON_2 else str(result, 'utf-8')
    result = str(result).strip()
    assert result.startswith('<?xml')
    assert result.endswith('</alto>')


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] >= (4, 1),
    reason='requires tesseract < 4.1',
)
def test_image_to_alto_xml_support(test_file):
    with pytest.raises(ALTONotSupported):
        image_to_alto_xml(test_file)


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] >= (3, 5),
    reason='requires tesseract < 3.05',
)
def test_image_to_data__pandas_support(test_file_small):
    with pytest.raises(TSVNotSupported):
        image_to_data(test_file_small, output_type=Output.DATAFRAME)


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05',
)
@pytest.mark.skipif(pandas_installed is False, reason='requires pandas')
def test_image_to_data__pandas_output(test_file_small):
    """Test and compare the type and meta information of the result."""
    result = image_to_data(test_file_small, output_type=Output.DATAFRAME)
    assert isinstance(result, pandas.DataFrame)
    expected_columns = [
        'level',
        'page_num',
        'block_num',
        'par_num',
        'line_num',
        'word_num',
        'left',
        'top',
        'width',
        'height',
        'conf',
        'text',
    ]
    assert bool(set(result.columns).intersection(expected_columns))


@pytest.mark.skipif(
    TESSERACT_VERSION[:2] < (3, 5),
    reason='requires tesseract >= 3.05',
)
@pytest.mark.parametrize(
    'output',
    [Output.BYTES, Output.DICT, Output.STRING],
    ids=['bytes', 'dict', 'string'],
)
def test_image_to_data_common_output(test_file_small, output):
    """Test and compare the type of the result."""
    result = image_to_data(test_file_small, output_type=output)
    expected_dict_result = {
        'level': [1, 2, 3, 4, 5],
        'page_num': [1, 1, 1, 1, 1],
        'block_num': [0, 1, 1, 1, 1],
        'par_num': [0, 0, 1, 1, 1],
        'line_num': [0, 0, 0, 1, 1],
        'word_num': [0, 0, 0, 0, 1],
        'left': [0, 11, 11, 11, 11],
        'top': [0, 11, 11, 11, 11],
        'width': [79, 60, 60, 60, 60],
        'height': [47, 24, 24, 24, 24],
        # 'conf': ['-1', '-1', '-1', '-1', 96],
        'text': ['', '', '', '', 'This'],
    }

    if output is Output.BYTES:
        assert isinstance(result, bytes)

    elif output is Output.DICT:
        confidence_values = result.pop('conf', None)
        assert confidence_values is not None
        assert 0 <= confidence_values[-1] <= 100
        assert result == expected_dict_result

    elif output is Output.STRING:
        assert isinstance(result, string_type)
        for key in expected_dict_result.keys():
            assert key in result


@pytest.mark.parametrize('obj', [1, 1.0, None], ids=['int', 'float', 'none'])
def test_wrong_prepare_type(obj):
    with pytest.raises(TypeError):
        prepare(obj)


@pytest.mark.parametrize(
    'test_path',
    [r'wrong_tesseract', getcwd() + path.sep + r'wrong_tesseract'],
    ids=['executable_name', 'absolute_path'],
)
def test_wrong_tesseract_cmd(monkeypatch, test_file, test_path):
    """Test wrong or missing tesseract command."""
    import pytesseract

    monkeypatch.setattr('pytesseract.pytesseract.tesseract_cmd', test_path)

    with pytest.raises(TesseractNotFoundError):
        pytesseract.get_languages.__wrapped__()

    with pytest.raises(TesseractNotFoundError):
        pytesseract.get_tesseract_version.__wrapped__()

    with pytest.raises(TesseractNotFoundError):
        pytesseract.image_to_string(test_file)


def test_main_not_found_cases(
    capsys,
    monkeypatch,
    test_file,
    test_invalid_file,
):
    """Test wrong or missing tesseract command in main."""
    import pytesseract

    monkeypatch.setattr('sys.argv', ['', test_invalid_file])
    assert pytesseract.pytesseract.main() == 1
    captured_stderr = capsys.readouterr().err
    assert (
        'No such file or directory' in captured_stderr
        and test_invalid_file in captured_stderr
    )

    monkeypatch.setattr(
        'pytesseract.pytesseract.tesseract_cmd',
        'wrong_tesseract',
    )
    monkeypatch.setattr('sys.argv', ['', test_file])
    assert pytesseract.pytesseract.main() == 1
    assert (
        "is not installed or it's not in your PATH" in capsys.readouterr().err
    )

    monkeypatch.setattr('sys.argv', [''])
    assert pytesseract.pytesseract.main() == 2
    assert 'Usage: pytesseract [-l lang] input_file' in capsys.readouterr().err


@pytest.mark.parametrize(
    'test_path',
    [path.sep + r'wrong_tesseract', r''],
    ids=['permission_error_path', 'invalid_path'],
)
def test_proper_oserror_exception_handling(monkeypatch, test_file, test_path):
    """ "Test for bubbling up OSError exceptions."""
    import pytesseract

    monkeypatch.setattr(
        'pytesseract.pytesseract.tesseract_cmd',
        test_path,
    )

    with pytest.raises(
        TesseractNotFoundError if IS_PYTHON_2 and test_path else OSError,
    ):
        pytesseract.image_to_string(test_file)


DEFAULT_LANGUAGES = ('fra', 'eng', 'osd')


@pytest.mark.parametrize(
    'test_config,expected',
    [
        ('', DEFAULT_LANGUAGES),
        (f'--tessdata-dir {TESSDATA_DIR}/', ('dzo_test', 'eng')),
        ('--tessdata-dir /dev/null', ()),
        ('--tessdata-dir invalid_path/', ()),
        ('--tessdata-dir=invalid_config/', DEFAULT_LANGUAGES),
    ],
    ids=[
        'default_empty_config',
        'custom_tessdata_dir',
        'incorrect_tessdata_dir',
        'invalid_tessdata_dir',
        'invalid_config',
    ],
)
def test_get_languages(test_config, expected):
    result = get_languages.__wrapped__(test_config)
    if not result:
        assert result == []

    for lang in expected:
        assert lang in result


@pytest.mark.parametrize(
    ('input_args', 'expected'),
    (
        (('', ' ', 0), {}),
        (('\n', '\n', 0), {}),
        (('header1 header2 header3\n', '\t', 0), {}),
    ),
)
def test_file_to_dict(input_args, expected):
    assert file_to_dict(*input_args) == expected


@pytest.mark.parametrize(
    ('tesseract_version', 'expected'),
    (
        (b'3.5.0', '3.5.0'),
        (b'4.1-a8s6f8d3f', '4.1'),
        (b'v4.0.0-beta1.9', '4.0.0'),
    ),
)
def test_get_tesseract_version(tesseract_version, expected):
    with mock.patch('subprocess.check_output', spec=True) as output_mock:
        output_mock.return_value = tesseract_version
        assert get_tesseract_version.__wrapped__().public == expected


@pytest.mark.parametrize(
    ('tesseract_version', 'expected_msg'),
    (
        (b'', 'Invalid tesseract version: ""'),
        (b'invalid', 'Invalid tesseract version: "invalid"'),
    ),
)
def test_get_tesseract_version_invalid(tesseract_version, expected_msg):
    with mock.patch('subprocess.check_output', spec=True) as output_mock:
        output_mock.return_value = tesseract_version
        with pytest.raises(SystemExit) as e:
            get_tesseract_version.__wrapped__()

        (msg,) = e.value.args
        assert msg == expected_msg
