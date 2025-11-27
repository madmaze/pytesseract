"""Test various image formats and conversions for pytesseract."""
from __future__ import annotations

import pytest
from PIL import Image

from pytesseract import image_to_boxes
from pytesseract import image_to_data
from pytesseract import image_to_string
from pytesseract import Output


pytestmark = pytest.mark.pytesseract


class TestImageModes:
    """Test different PIL image modes."""

    def test_rgb_mode(self):
        """Test RGB mode image."""
        img = Image.new('RGB', (100, 100), color='white')
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_rgba_mode(self):
        """Test RGBA mode image with transparency."""
        img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 200))
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_l_mode_grayscale(self):
        """Test L mode (grayscale) image."""
        img = Image.new('L', (100, 100), color=128)
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_la_mode_grayscale_alpha(self):
        """Test LA mode (grayscale with alpha) image."""
        img = Image.new('LA', (100, 100), color=(128, 200))
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_p_mode_palette(self):
        """Test P mode (palette) image."""
        img = Image.new('P', (100, 100), color=0)
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_cmyk_mode(self):
        """Test CMYK mode image."""
        img = Image.new('CMYK', (100, 100), color=(0, 0, 0, 0))
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_1_mode_binary(self):
        """Test 1 mode (binary/black and white) image."""
        img = Image.new('1', (100, 100), color=1)
        result = image_to_string(img)
        assert isinstance(result, str)


class TestImageConversions:
    """Test image format conversions."""

    def test_convert_rgba_to_rgb(self):
        """Test RGBA to RGB conversion."""
        img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_convert_cmyk_to_rgb(self):
        """Test CMYK to RGB conversion."""
        img = Image.new('CMYK', (100, 100), color=(0, 0, 0, 0))
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_convert_palette_to_rgb(self):
        """Test palette to RGB conversion."""
        img = Image.new('P', (100, 100))
        result = image_to_string(img)
        assert isinstance(result, str)


class TestImageSizes:
    """Test various image sizes."""

    @pytest.mark.parametrize(
        'size',
        [
            (1, 1),
            (10, 10),
            (50, 50),
            (100, 100),
            (500, 500),
            (1000, 1000),
        ],
    )
    def test_square_images(self, size):
        """Test square images of various sizes."""
        img = Image.new('RGB', size, color='white')
        result = image_to_string(img)
        assert isinstance(result, str)

    @pytest.mark.parametrize(
        'size',
        [
            (100, 50),
            (50, 100),
            (200, 100),
            (100, 200),
            (1000, 100),
            (100, 1000),
        ],
    )
    def test_rectangular_images(self, size):
        """Test rectangular images with various aspect ratios."""
        img = Image.new('RGB', size, color='white')
        result = image_to_string(img)
        assert isinstance(result, str)

    @pytest.mark.slow
    def test_very_wide_image(self):
        """Test very wide image."""
        img = Image.new('RGB', (5000, 100), color='white')
        result = image_to_string(img)
        assert isinstance(result, str)

    @pytest.mark.slow
    def test_very_tall_image(self):
        """Test very tall image."""
        img = Image.new('RGB', (100, 5000), color='white')
        result = image_to_string(img)
        assert isinstance(result, str)


class TestImageDPI:
    """Test images with different DPI settings."""

    def test_low_dpi_image(self):
        """Test image with low DPI (72)."""
        img = Image.new('RGB', (100, 100), color='white')
        img.info['dpi'] = (72, 72)
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_standard_dpi_image(self):
        """Test image with standard DPI (96)."""
        img = Image.new('RGB', (100, 100), color='white')
        img.info['dpi'] = (96, 96)
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_high_dpi_image(self):
        """Test image with high DPI (300)."""
        img = Image.new('RGB', (100, 100), color='white')
        img.info['dpi'] = (300, 300)
        result = image_to_string(img)
        assert isinstance(result, str)

    def test_very_high_dpi_image(self):
        """Test image with very high DPI (600)."""
        img = Image.new('RGB', (100, 100), color='white')
        img.info['dpi'] = (600, 600)
        result = image_to_string(img)
        assert isinstance(result, str)


class TestImageRotation:
    """Test rotated images."""

    @pytest.mark.parametrize('angle', [0, 90, 180, 270])
    def test_rotated_images(self, text_image, angle):
        """Test images rotated at various angles."""
        rotated = text_image.rotate(angle, expand=True)
        result = image_to_string(rotated)
        assert isinstance(result, str)

    def test_arbitrary_rotation(self, text_image):
        """Test image rotated at arbitrary angle."""
        rotated = text_image.rotate(45, expand=True, fillcolor='white')
        result = image_to_string(rotated)
        assert isinstance(result, str)


class TestImageQuality:
    """Test images with different quality settings."""

    def test_high_quality_image(self, text_image, temp_dir):
        """Test high quality JPEG image."""
        jpeg_path = temp_dir / 'high_quality.jpg'
        text_image.save(jpeg_path, quality=95)
        result = image_to_string(str(jpeg_path))
        assert isinstance(result, str)

    def test_low_quality_image(self, text_image, temp_dir):
        """Test low quality JPEG image."""
        jpeg_path = temp_dir / 'low_quality.jpg'
        text_image.save(jpeg_path, quality=10)
        result = image_to_string(str(jpeg_path))
        assert isinstance(result, str)

    def test_compressed_png(self, text_image, temp_dir):
        """Test compressed PNG image."""
        png_path = temp_dir / 'compressed.png'
        text_image.save(png_path, compress_level=9)
        result = image_to_string(str(png_path))
        assert isinstance(result, str)


class TestNumpyArrays:
    """Test NumPy array inputs."""

    @pytest.mark.skipif(
        not pytest.importorskip('numpy', reason='numpy not installed'),
        reason='numpy not available',
    )
    def test_numpy_array_rgb(self):
        """Test RGB NumPy array."""
        import numpy as np

        arr = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = image_to_string(arr)
        assert isinstance(result, str)

    @pytest.mark.skipif(
        not pytest.importorskip('numpy', reason='numpy not installed'),
        reason='numpy not available',
    )
    def test_numpy_array_grayscale(self):
        """Test grayscale NumPy array."""
        import numpy as np

        arr = np.ones((100, 100), dtype=np.uint8) * 128
        result = image_to_string(arr)
        assert isinstance(result, str)

    @pytest.mark.skipif(
        not pytest.importorskip('numpy', reason='numpy not installed'),
        reason='numpy not available',
    )
    def test_numpy_array_from_pil(self, text_image):
        """Test NumPy array created from PIL image."""
        import numpy as np

        arr = np.array(text_image)
        result = image_to_string(arr)
        assert isinstance(result, str)


class TestAllOutputFormats:
    """Test all output formats with various image types."""

    def test_string_output_all_formats(self, text_image):
        """Test STRING output with different image formats."""
        result = image_to_string(text_image, output_type=Output.STRING)
        assert isinstance(result, str)

    def test_bytes_output_all_formats(self, text_image):
        """Test BYTES output with different image formats."""
        result = image_to_string(text_image, output_type=Output.BYTES)
        assert isinstance(result, bytes)

    def test_dict_output_all_formats(self, text_image):
        """Test DICT output with different image formats."""
        result = image_to_string(text_image, output_type=Output.DICT)
        assert isinstance(result, dict)

    def test_boxes_all_formats(self, text_image):
        """Test boxes output with different image formats."""
        result = image_to_boxes(text_image)
        assert isinstance(result, str)

    def test_data_all_formats(self, text_image):
        """Test data output with different image formats."""
        result = image_to_data(text_image)
        assert isinstance(result, str)
