import os.path

import pytest

from pytesseract import image_to_string

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


@pytest.mark.pytesseract
def test_quick_brown_dog_image():
    test_file = os.path.join(DATA_DIR, 'test.png')

    # Don't perform assertion against full string in case the version
    # of tesseract installed doesn't catch it all. This test is testing
    # that pytesseract command line program is called correctly.
    assert 'The quick brown dog' in image_to_string(test_file, 'eng')


@pytest.mark.pytesseract
@pytest.mark.lang_fra
def test_european_image():
    test_file = os.path.join(DATA_DIR, 'test-european.jpg')

    assert 'La volpe marrone' in image_to_string(test_file, 'fra')
