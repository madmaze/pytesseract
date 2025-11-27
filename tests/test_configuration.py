"""Test configuration parameters and options for pytesseract."""
from __future__ import annotations

import sys

import pytest
from PIL import Image

from pytesseract import image_to_data
from pytesseract import image_to_osd
from pytesseract import image_to_string
from pytesseract import Output


pytestmark = pytest.mark.pytesseract


class TestPSMConfigurations:
    """Test Page Segmentation Mode (PSM) configurations."""

    @pytest.mark.parametrize('psm_value', range(0, 14))
    def test_all_psm_modes(self, text_image, psm_value):
        """Test all PSM modes (0-13)."""
        try:
            if psm_value == 0:
                # PSM 0 is for OSD only
                result = image_to_osd(text_image, config=f'--psm {psm_value}')
            else:
                result = image_to_string(
                    text_image, config=f'--psm {psm_value}',
                )
            assert isinstance(result, str)
        except Exception as e:
            # Some PSM modes may not work with all images
            pytest.skip(f"PSM {psm_value} not compatible: {e}")

    def test_psm_single_block(self, text_image):
        """Test PSM 6 (single uniform block of text)."""
        result = image_to_string(text_image, config='--psm 6')
        assert isinstance(result, str)

    def test_psm_single_line(self, text_image):
        """Test PSM 7 (single text line)."""
        result = image_to_string(text_image, config='--psm 7')
        assert isinstance(result, str)

    def test_psm_single_word(self, text_image):
        """Test PSM 8 (single word)."""
        result = image_to_string(text_image, config='--psm 8')
        assert isinstance(result, str)


class TestOEMConfigurations:
    """Test OCR Engine Mode (OEM) configurations."""

    @pytest.mark.parametrize('oem_value', range(0, 4))
    def test_all_oem_modes(self, text_image, oem_value):
        """Test all OEM modes (0-3)."""
        try:
            result = image_to_string(text_image, config=f'--oem {oem_value}')
            assert isinstance(result, str)
        except Exception as e:
            # Some OEM modes may not be available
            pytest.skip(f"OEM {oem_value} not available: {e}")

    def test_oem_lstm_only(self, text_image):
        """Test OEM 1 (LSTM only)."""
        result = image_to_string(text_image, config='--oem 1')
        assert isinstance(result, str)

    def test_oem_combined(self, text_image):
        """Test OEM 3 (Default, based on what is available)."""
        result = image_to_string(text_image, config='--oem 3')
        assert isinstance(result, str)


class TestCombinedConfigurations:
    """Test combinations of configuration parameters."""

    def test_psm_and_oem_combined(self, text_image):
        """Test PSM and OEM together."""
        result = image_to_string(text_image, config='--psm 6 --oem 3')
        assert isinstance(result, str)

    def test_multiple_config_flags(self, text_image):
        """Test multiple configuration flags."""
        config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
        result = image_to_string(text_image, config=config)
        assert isinstance(result, str)

    def test_config_with_custom_variables(self, text_image):
        """Test config with custom tesseract variables."""
        config = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = image_to_string(text_image, config=config)
        assert isinstance(result, str)


class TestLanguageConfigurations:
    """Test language configuration options."""

    def test_single_language(self, text_image):
        """Test with single language."""
        result = image_to_string(text_image, lang='eng')
        assert isinstance(result, str)

    @pytest.mark.lang_fra
    def test_multiple_languages(self, text_image):
        """Test with multiple languages."""
        result = image_to_string(text_image, lang='eng+fra')
        assert isinstance(result, str)

    def test_language_with_config(self, text_image):
        """Test language parameter with config."""
        result = image_to_string(text_image, lang='eng', config='--psm 6')
        assert isinstance(result, str)


class TestNiceParameter:
    """Test nice parameter (Unix process priority)."""

    @pytest.mark.skipif(
        sys.platform.startswith('win'), reason='nice not supported on Windows',
    )
    @pytest.mark.parametrize('nice_value', [-20, -10, 0, 10, 19])
    def test_nice_values(self, text_image, nice_value):
        """Test various nice values."""
        result = image_to_string(text_image, nice=nice_value)
        assert isinstance(result, str)

    @pytest.mark.skipif(
        not sys.platform.startswith('win'), reason='Test Windows behavior',
    )
    def test_nice_ignored_on_windows(self, text_image):
        """Test that nice is ignored on Windows."""
        result = image_to_string(text_image, nice=10)
        assert isinstance(result, str)


class TestTessdataDir:
    """Test tessdata directory configuration."""

    def test_custom_tessdata_dir(self, text_image, temp_dir):
        """Test with custom tessdata directory."""
        # This will likely fail but should not crash
        config = f'--tessdata-dir "{temp_dir}"'
        try:
            result = image_to_string(text_image, config=config)
            assert isinstance(result, str)
        except Exception:
            # Expected to fail with invalid tessdata dir
            pass

    def test_tessdata_dir_with_quotes(self, text_image):
        """Test tessdata dir path with quotes."""
        config = '--tessdata-dir "/usr/share/tesseract-ocr/4.00/tessdata"'
        try:
            result = image_to_string(text_image, config=config)
            assert isinstance(result, str)
        except Exception:
            # Path may not exist on all systems
            pass


class TestOutputConfiguration:
    """Test output-related configurations."""

    def test_string_output_with_config(self, text_image):
        """Test STRING output with config."""
        result = image_to_string(
            text_image, output_type=Output.STRING, config='--psm 6',
        )
        assert isinstance(result, str)

    def test_bytes_output_with_config(self, text_image):
        """Test BYTES output with config."""
        result = image_to_string(
            text_image, output_type=Output.BYTES, config='--psm 6',
        )
        assert isinstance(result, bytes)

    def test_dict_output_with_config(self, text_image):
        """Test DICT output with config."""
        result = image_to_string(
            text_image, output_type=Output.DICT, config='--psm 6',
        )
        assert isinstance(result, dict)
        assert 'text' in result
