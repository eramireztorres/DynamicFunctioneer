"""
Unit tests for code storage components.
"""

import os
import tempfile
import pytest
from pathlib import Path
from dynamic_functioneer.code_management.code_storage import CodeFileManager, DynamicTestFileManager


class TestCodeFileManager:
    """Test CodeFileManager class."""

    def test_save_and_load_code(self, tmp_path):
        """Test saving and loading code."""
        file_path = tmp_path / "test_code.py"
        manager = CodeFileManager(str(file_path))

        code = "def test_function():\n    return 42"
        manager.save_code(code)

        assert file_path.exists()
        loaded = manager.load_code()
        assert loaded == code

    def test_code_exists(self, tmp_path):
        """Test code_exists method."""
        file_path = tmp_path / "test_code.py"
        manager = CodeFileManager(str(file_path))

        assert not manager.code_exists()

        manager.save_code("test code")
        assert manager.code_exists()

    def test_delete_code(self, tmp_path):
        """Test deleting code file."""
        file_path = tmp_path / "test_code.py"
        manager = CodeFileManager(str(file_path))

        manager.save_code("test code")
        assert file_path.exists()

        manager.delete_code()
        assert not file_path.exists()

    def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting a file that doesn't exist."""
        file_path = tmp_path / "nonexistent.py"
        manager = CodeFileManager(str(file_path))

        # Should not raise an error
        manager.delete_code()

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading a file that doesn't exist."""
        file_path = tmp_path / "nonexistent.py"
        manager = CodeFileManager(str(file_path))

        with pytest.raises(FileNotFoundError):
            manager.load_code()

    def test_save_creates_directory(self, tmp_path):
        """Test that save_code creates parent directories."""
        nested_path = tmp_path / "nested" / "deep" / "test.py"
        manager = CodeFileManager(str(nested_path))

        manager.save_code("test code")
        assert nested_path.exists()
        assert nested_path.parent.exists()


class TestDynamicTestFileManager:
    """Test DynamicTestFileManager class."""

    def test_save_test_file(self, tmp_path):
        """Test saving a test file."""
        manager = DynamicTestFileManager(str(tmp_path))

        test_code = "import unittest\n\nclass TestExample(unittest.TestCase):\n    pass"
        test_path = tmp_path / "test_example.py"

        manager.save_test_file(str(test_path), test_code)

        assert test_path.exists()
        assert test_path.read_text() == test_code

    def test_get_test_file_path(self, tmp_path):
        """Test generating test file path."""
        manager = DynamicTestFileManager(str(tmp_path))

        path = manager.get_test_file_path("my_function")
        assert path == str(tmp_path / "test_my_function.py")

    def test_get_test_file_path_custom_dir(self, tmp_path):
        """Test generating test file path with custom directory."""
        manager = DynamicTestFileManager(str(tmp_path))
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()

        path = manager.get_test_file_path("my_function", str(custom_dir))
        assert path == str(custom_dir / "test_my_function.py")

    def test_save_test_file_creates_directory(self, tmp_path):
        """Test that save_test_file creates parent directories."""
        manager = DynamicTestFileManager(str(tmp_path))
        nested_path = tmp_path / "nested" / "test_file.py"

        manager.save_test_file(str(nested_path), "test code")

        assert nested_path.exists()
        assert nested_path.parent.exists()
