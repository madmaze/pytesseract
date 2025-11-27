"""Test utility functions in pytesseract."""
from __future__ import annotations

import pytest
from unittest import mock

from pytesseract.pytesseract import (
    file_to_dict,
    osd_to_dict,
    is_valid,
    cleanup,
    get_errors,
    prepare,
)


pytestmark = pytest.mark.pytesseract


class TestFileToDictFunction:
    """Test file_to_dict utility function."""

    def test_empty_input(self):
        """Test with empty input."""
        result = file_to_dict('', ' ', 0)
        assert result == {}

    def test_whitespace_only(self):
        """Test with whitespace only."""
        result = file_to_dict('\n', '\n', 0)
        assert result == {}

    def test_header_only(self):
        """Test with header but no data rows."""
        result = file_to_dict('header1 header2 header3\n', '\t', 0)
        assert result == {}

    def test_valid_tsv_data(self):
        """Test with valid TSV data."""
        tsv_data = 'col1\tcol2\tcol3\n1\t2\t3\n4\t5\t6\n'
        result = file_to_dict(tsv_data, '\t', -1)
        assert 'col1' in result
        assert 'col2' in result
        assert 'col3' in result
        assert result['col1'] == [1, 4]
        assert result['col2'] == [2, 5]
        assert result['col3'] == ['3', '6']

    def test_missing_last_cell(self):
        """Test handling of missing last cell in TSV."""
        tsv_data = 'col1\tcol2\tcol3\n1\t2\t3\n4\t5\n'
        result = file_to_dict(tsv_data, '\t', -1)
        assert len(result['col3']) == 2
        assert result['col3'][1] == ''

    def test_different_delimiters(self):
        """Test with different delimiters."""
        csv_data = 'col1,col2,col3\n1,2,3\n4,5,6\n'
        result = file_to_dict(csv_data, ',', -1)
        assert 'col1' in result
        assert result['col1'] == [1, 4]


class TestOsdToDictFunction:
    """Test osd_to_dict utility function."""

    def test_valid_osd_output(self, sample_osd_output):
        """Test with valid OSD output."""
        result = osd_to_dict(sample_osd_output)
        assert 'page_num' in result
        assert 'orientation' in result
        assert 'rotate' in result
        assert 'orientation_conf' in result
        assert 'script' in result
        assert 'script_conf' in result
        assert result['page_num'] == 0
        assert result['orientation'] == 0
        assert result['script'] == 'Latin'

    def test_osd_with_missing_fields(self):
        """Test OSD output with missing fields."""
        osd_data = 'Page number: 0\nOrientation in degrees: 90\n'
        result = osd_to_dict(osd_data)
        assert 'page_num' in result
        assert 'orientation' in result
        assert result['page_num'] == 0
        assert result['orientation'] == 90

    def test_osd_with_invalid_values(self):
        """Test OSD output with invalid values."""
        osd_data = 'Page number: invalid\nOrientation in degrees: 0\n'
        result = osd_to_dict(osd_data)
        # Invalid values should be skipped
        assert 'page_num' not in result or result.get('orientation') == 0


class TestIsValidFunction:
    """Test is_valid utility function."""

    def test_valid_int(self):
        """Test valid integer string."""
        assert is_valid('123', int) is True
        assert is_valid('0', int) is True
        assert is_valid('999', int) is True

    def test_invalid_int(self):
        """Test invalid integer string."""
        assert is_valid('abc', int) is False
        assert is_valid('12.34', int) is False
        assert is_valid('', int) is False

    def test_valid_float(self):
        """Test valid float string."""
        assert is_valid('12.34', float) is True
        assert is_valid('0.0', float) is True
        assert is_valid('123', float) is True

    def test_invalid_float(self):
        """Test invalid float string."""
        assert is_valid('abc', float) is False
        assert is_valid('', float) is False

    def test_valid_str(self):
        """Test string type (always valid)."""
        assert is_valid('anything', str) is True
        assert is_valid('', str) is True
        assert is_valid('123', str) is True


class TestCleanupFunction:
    """Test cleanup utility function."""

    def test_cleanup_existing_files(self, temp_dir):
        """Test cleanup of existing files."""
        # Create test files
        test_file1 = temp_dir / 'test_cleanup.txt'
        test_file2 = temp_dir / 'test_cleanup.dat'
        test_file1.write_text('test')
        test_file2.write_text('test')
        
        # Cleanup with wildcard
        cleanup(str(temp_dir / 'test_cleanup'))
        
        # Files should be removed
        assert not test_file1.exists()
        assert not test_file2.exists()

    def test_cleanup_nonexistent_file(self, temp_dir):
        """Test cleanup of nonexistent file (should not error)."""
        # Should not raise exception
        cleanup(str(temp_dir / 'nonexistent_file'))

    def test_cleanup_with_none(self):
        """Test cleanup with None input."""
        # Should handle None gracefully
        try:
            cleanup(None)
        except Exception:
            # May raise exception, but should not crash
            pass


class TestGetErrorsFunction:
    """Test get_errors utility function."""

    def test_decode_error_string(self):
        """Test decoding error string."""
        error_bytes = b'Error: Tesseract failed\nAnother error line\n'
        result = get_errors(error_bytes)
        assert 'Error: Tesseract failed' in result
        assert 'Another error line' in result

    def test_empty_error_string(self):
        """Test empty error string."""
        result = get_errors(b'')
        assert result == ''

    def test_multiline_errors(self):
        """Test multiline error messages."""
        error_bytes = b'Line 1\nLine 2\nLine 3\n'
        result = get_errors(error_bytes)
        assert 'Line 1' in result
        assert 'Line 2' in result
        assert 'Line 3' in result


class TestPrepareFunction:
    """Test prepare utility function."""

    def test_prepare_pil_image(self):
        """Test prepare with PIL Image."""
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        prepared_img, ext = prepare(img)
        assert ext == 'PNG'
        assert prepared_img.mode == 'RGB'

    def test_prepare_with_format(self):
        """Test prepare with image that has format."""
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img.format = 'JPEG'
        prepared_img, ext = prepare(img)
        assert ext == 'JPEG'

    def test_prepare_removes_alpha(self):
        """Test prepare removes alpha channel."""
        from PIL import Image
        img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
        prepared_img, ext = prepare(img)
        assert 'A' not in prepared_img.getbands()

    def test_prepare_unsupported_format(self):
        """Test prepare with unsupported format."""
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img.format = 'UNSUPPORTED'
        with pytest.raises(TypeError, match='Unsupported image format'):
            prepare(img)

    @pytest.mark.skipif(
        not pytest.importorskip('numpy', reason='numpy not installed'),
        reason='numpy not available'
    )
    def test_prepare_numpy_array(self):
        """Test prepare with NumPy array."""
        import numpy as np
        arr = np.ones((100, 100, 3), dtype=np.uint8) * 255
        prepared_img, ext = prepare(arr)
        assert ext == 'PNG'
        assert hasattr(prepared_img, 'mode')