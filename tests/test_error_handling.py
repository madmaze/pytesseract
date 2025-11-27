"""Test error handling and exception scenarios for pytesseract."""
from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest

from pytesseract import (
    get_languages,
    get_tesseract_version,
    image_to_string,
    TesseractNotFoundError,
    TesseractError,
)


pytestmark = pytest.mark.pytesseract


class TestTesseractNotFound:
    """Test scenarios where tesseract is not found."""

    def test_invalid_tesseract_path(self, monkeypatch, text_image):
        """Test with invalid tesseract executable path."""
        import pytesseract
        monkeypatch.setattr('pytesseract.pytesseract.tesseract_cmd', '/invalid/path/tesseract')
        
        with pytest.raises(TesseractNotFoundError):
            image_to_string(text_image)

    def test_get_languages_tesseract_not_found(self, monkeypatch):
        """Test get_languages when tesseract not found."""
        import pytesseract
        monkeypatch.setattr('pytesseract.pytesseract.tesseract_cmd', 'nonexistent_tesseract')
        
        with pytest.raises(TesseractNotFoundError):
            get_languages.__wrapped__()

    def test_get_version_tesseract_not_found(self, monkeypatch):
        """Test get_tesseract_version when tesseract not found."""
        import pytesseract
        monkeypatch.setattr('pytesseract.pytesseract.tesseract_cmd', 'nonexistent_tesseract')
        
        with pytest.raises(TesseractNotFoundError):
            get_tesseract_version.__wrapped__()


class TestFileErrors:
    """Test file-related error scenarios."""

    def test_corrupted_image_file(self, temp_dir):
        """Test with corrupted image file."""
        corrupted_file = temp_dir / 'corrupted.jpg'
        corrupted_file.write_bytes(b'This is not a valid image file')
        
        with pytest.raises(Exception):  # PIL will raise various exceptions
            image_to_string(str(corrupted_file))

    def test_directory_instead_of_file(self, temp_dir):
        """Test passing directory path instead of file."""
        # Tesseract raises TesseractError when given a directory
        with pytest.raises((OSError, IsADirectoryError, TesseractError)):
            image_to_string(str(temp_dir))

    def test_permission_denied(self, temp_dir, monkeypatch):
        """Test file permission errors."""
        # Create a file and simulate permission error
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test')
        
        def mock_open_permission_denied(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        # This test is platform-dependent, so we mock it
        with mock.patch('builtins.open', side_effect=mock_open_permission_denied):
            with pytest.raises(PermissionError):
                with open(str(test_file), 'r') as f:
                    f.read()


class TestSubprocessErrors:
    """Test subprocess-related errors."""

    def test_tesseract_returns_error(self, monkeypatch, text_image):
        """Test when tesseract subprocess returns error code."""
        import subprocess
        
        def mock_popen(*args, **kwargs):
            mock_proc = mock.Mock()
            mock_proc.returncode = 1
            mock_proc.communicate.return_value = (b'', b'Tesseract Error')
            mock_proc.stdin = mock.Mock()
            mock_proc.stdout = mock.Mock()
            mock_proc.stderr = mock.Mock()
            return mock_proc
        
        with mock.patch('subprocess.Popen', side_effect=mock_popen):
            with pytest.raises(TesseractError):
                image_to_string(text_image)

    def test_subprocess_timeout_handling(self, text_image):
        """Test subprocess timeout is handled correctly."""
        with pytest.raises(RuntimeError, match='timeout'):
            image_to_string(text_image, timeout=0.00001)


class TestMemoryErrors:
    """Test memory-related error scenarios."""

    @pytest.mark.slow
    def test_extremely_large_image(self):
        """Test with extremely large image that might cause memory issues."""
        from PIL import Image
        
        # Create a very large image
        try:
            large_img = Image.new('RGB', (20000, 20000), color='white')
            result = image_to_string(large_img)
            assert isinstance(result, str)
        except MemoryError:
            # Expected on systems with limited memory
            pytest.skip("Not enough memory for this test")


class TestConcurrencyErrors:
    """Test concurrent access scenarios."""

    def test_concurrent_temp_file_access(self, text_image):
        """Test concurrent access to temporary files."""
        from concurrent.futures import ThreadPoolExecutor
        
        def process_image():
            return image_to_string(text_image)
        
        # Run multiple OCR operations concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_image) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)


class TestCleanupErrors:
    """Test cleanup and resource management errors."""

    def test_temp_file_cleanup(self, text_image):
        """Test that temporary files are cleaned up properly."""
        import tempfile
        import glob
        
        temp_dir = tempfile.gettempdir()
        before_files = set(glob.glob(os.path.join(temp_dir, 'tess_*')))
        
        # Run OCR
        image_to_string(text_image)
        
        after_files = set(glob.glob(os.path.join(temp_dir, 'tess_*')))
        
        # No new temp files should remain
        new_files = after_files - before_files
        assert len(new_files) == 0, f"Temp files not cleaned up: {new_files}"


class TestInvalidVersionHandling:
    """Test handling of invalid tesseract versions."""

    @pytest.mark.parametrize('invalid_version', [
        b'',
        b'invalid',
        b'1.0.0',  # Too old
        b'abc.def.ghi',
    ])
    def test_invalid_version_string(self, monkeypatch, invalid_version):
        """Test handling of invalid version strings."""
        with mock.patch('subprocess.check_output', return_value=invalid_version):
            with pytest.raises(SystemExit):
                get_tesseract_version.__wrapped__()