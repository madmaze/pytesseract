"""Shared pytest fixtures for pytesseract tests."""
from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest
from PIL import Image


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's cleaned up after test."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / 'data'


@pytest.fixture
def blank_image():
    """Create a blank white image."""
    img = Image.new('RGB', (100, 100), color='white')
    return img


@pytest.fixture
def black_image():
    """Create a blank black image."""
    img = Image.new('RGB', (100, 100), color='black')
    return img


@pytest.fixture
def rgba_image():
    """Create an RGBA image with alpha channel."""
    img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
    return img


@pytest.fixture
def grayscale_image():
    """Create a grayscale image."""
    img = Image.new('L', (100, 100), color=128)
    return img


@pytest.fixture
def cmyk_image():
    """Create a CMYK image."""
    img = Image.new('CMYK', (100, 100), color=(0, 0, 0, 0))
    return img


@pytest.fixture
def tiny_image():
    """Create a very small image (1x1)."""
    img = Image.new('RGB', (1, 1), color='white')
    return img


@pytest.fixture
def large_image():
    """Create a large image for stress testing."""
    img = Image.new('RGB', (5000, 5000), color='white')
    return img


@pytest.fixture
def text_image():
    """Create an image with text for testing."""
    from PIL import ImageDraw, ImageFont

    img = Image.new('RGB', (200, 50), color='white')
    draw = ImageDraw.Draw(img)
    try:
        # Try to use a default font
        draw.text((10, 10), 'Test Text', fill='black')
    except Exception:
        # Fallback if font not available
        pass
    return img


@pytest.fixture
def mock_tesseract_output():
    """Mock tesseract command output."""
    return b'This is test output'


@pytest.fixture
def mock_tesseract_version():
    """Mock tesseract version output."""
    return b'tesseract 4.1.1'


@pytest.fixture
def mock_languages_output():
    """Mock tesseract --list-langs output."""
    return b'List of available languages (3):\neng\nfra\nosd\n'


@pytest.fixture
def sample_osd_output():
    """Sample OSD (Orientation and Script Detection) output."""
    return (
        'Page number: 0\n'
        'Orientation in degrees: 0\n'
        'Rotate: 0\n'
        'Orientation confidence: 12.00\n'
        'Script: Latin\n'
        'Script confidence: 3.50\n'
    )


@pytest.fixture
def sample_tsv_output():
    """Sample TSV output from tesseract."""
    return (
        'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\t'
        'left\ttop\twidth\theight\tconf\ttext\n'
        '1\t1\t0\t0\t0\t0\t0\t0\t100\t50\t-1\t\n'
        '5\t1\t1\t1\t1\t1\t10\t10\t30\t15\t95\tTest\n'
    )


@pytest.fixture
def sample_box_output():
    """Sample box output from tesseract."""
    return (
        'T 10 20 30 40 0\n'
        'e 35 20 45 40 0\n'
        's 50 20 60 40 0\n'
        't 65 20 75 40 0\n'
    )
