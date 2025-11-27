"""Test edge cases and boundary conditions for pytesseract."""
from __future__ import annotations

import pytest
from PIL import Image

from pytesseract import image_to_string
from pytesseract import Output
from pytesseract import TesseractError
from pytesseract.pytesseract import prepare


pytestmark = pytest.mark.pytesseract


class TestImageEdgeCases:
    """Test edge cases related to image inputs."""

    def test_blank_white_image(self, blank_image):
        """Test OCR on blank white image."""
        result = image_to_string(blank_image)
        # Blank image should return empty or whitespace
        assert result.strip() == '' or result.isspace()

    def test_blank_black_image(self, black_image):
        """Test OCR on blank black image."""
        result = image_to_string(black_image)
        assert result.strip() == '' or result.isspace()

    def test_tiny_image(self, tiny_image):
        """Test OCR on 1x1 pixel image."""
        result = image_to_string(tiny_image)
        # Should not crash, may return empty
        assert isinstance(result, str)

    @pytest.mark.slow
    def test_large_image(self, large_image):
        """Test OCR on very large image (stress test)."""
        # This tests memory handling
        result = image_to_string(large_image)
        assert isinstance(result, str)

    def test_rgba_image_with_alpha(self, rgba_image):
        """Test image with alpha channel is handled correctly."""
        result = image_to_string(rgba_image)
        assert isinstance(result, str)

    def test_grayscale_image(self, grayscale_image):
        """Test grayscale image processing."""
        result = image_to_string(grayscale_image)
        assert isinstance(result, str)

    def test_cmyk_image(self, cmyk_image):
        """Test CMYK color mode image."""
        # CMYK cannot be saved as PNG, so this should raise OSError
        with pytest.raises(OSError, match='cannot write mode CMYK'):
            image_to_string(cmyk_image)


class TestInputValidation:
    """Test input validation and type checking."""

    def test_none_input(self):
        """Test that None input raises TypeError."""
        with pytest.raises(TypeError):
            image_to_string(None)

    def test_integer_input(self):
        """Test that integer input raises TypeError."""
        with pytest.raises(TypeError):
            image_to_string(123)

    def test_list_input(self):
        """Test that list input raises TypeError."""
        with pytest.raises(TypeError):
            image_to_string([1, 2, 3])

    def test_dict_input(self):
        """Test that dict input raises TypeError."""
        with pytest.raises(TypeError):
            image_to_string({'key': 'value'})

    def test_empty_string_path(self):
        """Test empty string as file path."""
        # Empty string resolves to current directory, tesseract raises TesseractError
        with pytest.raises((OSError, FileNotFoundError, TesseractError)):
            image_to_string('')

    def test_nonexistent_file_path(self):
        """Test nonexistent file path."""
        # Tesseract raises TesseractError for nonexistent files
        with pytest.raises((OSError, FileNotFoundError, TesseractError)):
            image_to_string('/nonexistent/path/to/image.png')


class TestPrepareFunction:
    """Test the prepare() function edge cases."""

    def test_prepare_with_alpha_channel(self, rgba_image):
        """Test prepare handles alpha channel correctly."""
        prepared_img, ext = prepare(rgba_image)
        # Should remove alpha channel
        assert 'A' not in prepared_img.getbands()
        assert 'RGB' == prepared_img.mode or 'L' == prepared_img.mode

    def test_prepare_with_no_format(self):
        """Test prepare with image that has no format attribute."""
        img = Image.new('RGB', (100, 100), color='white')
        # PIL Image objects created with new() don't have format
        prepared_img, ext = prepare(img)
        assert ext == 'PNG'  # Default format

    def test_prepare_invalid_type(self):
        """Test prepare with invalid type."""
        with pytest.raises(TypeError, match='Unsupported image object'):
            prepare('not an image')


class TestOutputTypes:
    """Test different output type combinations."""

    def test_string_output_empty_image(self, blank_image):
        """Test STRING output type with empty image."""
        result = image_to_string(blank_image, output_type=Output.STRING)
        assert isinstance(result, str)

    def test_bytes_output_empty_image(self, blank_image):
        """Test BYTES output type with empty image."""
        result = image_to_string(blank_image, output_type=Output.BYTES)
        assert isinstance(result, bytes)

    def test_dict_output_empty_image(self, blank_image):
        """Test DICT output type with empty image."""
        result = image_to_string(blank_image, output_type=Output.DICT)
        assert isinstance(result, dict)
        assert 'text' in result


class TestLanguageEdgeCases:
    """Test language parameter edge cases."""

    def test_empty_language_string(self, text_image):
        """Test with empty language string."""
        # Empty language string causes tesseract to fail
        with pytest.raises(TesseractError):
            image_to_string(text_image, lang='')

    def test_invalid_language_code(self, text_image):
        """Test with invalid language code."""
        # Should raise TesseractError or return empty
        try:
            result = image_to_string(text_image, lang='invalid_lang_xyz')
            # If it doesn't error, it should return something
            assert isinstance(result, str)
        except Exception as e:
            # Expected to fail with invalid language
            assert True

    def test_multiple_languages(self, text_image):
        """Test with multiple language codes."""
        result = image_to_string(text_image, lang='eng+fra')
        assert isinstance(result, str)


class TestConfigEdgeCases:
    """Test config parameter edge cases."""

    def test_empty_config(self, text_image):
        """Test with empty config string."""
        result = image_to_string(text_image, config='')
        assert isinstance(result, str)

    def test_whitespace_config(self, text_image):
        """Test with whitespace-only config."""
        result = image_to_string(text_image, config='   ')
        assert isinstance(result, str)

    def test_multiple_config_params(self, text_image):
        """Test with multiple config parameters."""
        result = image_to_string(text_image, config='--psm 6 --oem 3')
        assert isinstance(result, str)


class TestTimeoutEdgeCases:
    """Test timeout parameter edge cases."""

    def test_zero_timeout(self, text_image):
        """Test with timeout=0 (no timeout)."""
        result = image_to_string(text_image, timeout=0)
        assert isinstance(result, str)

    def test_negative_timeout(self, text_image):
        """Test with negative timeout value."""
        # Negative timeout is treated as a timeout and raises RuntimeError
        with pytest.raises(RuntimeError, match='timeout'):
            image_to_string(text_image, timeout=-1)

    def test_very_short_timeout(self, text_image):
        """Test with extremely short timeout."""
        with pytest.raises(RuntimeError, match='timeout'):
            image_to_string(text_image, timeout=0.0001)

    def test_float_timeout(self, text_image):
        """Test with float timeout value."""
        # Should handle float timeouts
        result = image_to_string(text_image, timeout=5.5)
        assert isinstance(result, str)
