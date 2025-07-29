import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

# Check for pathspec dependency
try:
    import pathspec
except ImportError:
    pathspec = None

from core.file_operations import (
    ensure_category_folder, 
    highlight_keyword,
    load_gitignore_patterns
)

class TestFileOperations(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_ensure_category_folder(self):
        """Test category folder creation."""
        folder = ensure_category_folder(self.test_dir, "android")
        expected_path = os.path.join(self.test_dir, "android")
        
        self.assertEqual(folder, expected_path)
        self.assertTrue(os.path.exists(folder))
        self.assertTrue(os.path.isdir(folder))
    
    def test_highlight_keyword(self):
        """Test keyword highlighting."""
        line = "This is a test coroutine example"
        highlighted = highlight_keyword(line, "coroutine")
        
        self.assertIn("\033[1;33mcoroutine\033[0m", highlighted)
        self.assertIn("This is a test", highlighted)
    
    def test_highlight_keyword_case_insensitive(self):
        """Test case-insensitive keyword highlighting."""
        line = "COROUTINE and coroutine"
        highlighted = highlight_keyword(line, "coroutine")
        
        # Should highlight both instances
        self.assertEqual(highlighted.count("\033[1;33m"), 2)
        self.assertEqual(highlighted.count("\033[0m"), 2)
    
    @patch('subprocess.run')
    def test_create_or_open_note_new_file(self, mock_subprocess):
        """Test creating a new note file."""
        from core.file_operations import create_or_open_note
        
        create_or_open_note(self.test_dir, "android", "2025-01-15", "code")
        
        expected_file = os.path.join(self.test_dir, "android", "2025-01-15.md")
        self.assertTrue(os.path.exists(expected_file))
        
        with open(expected_file, "r") as f:
            content = f.read()
            self.assertIn("# TIL - 2025-01-15", content)
            self.assertIn("- ", content)
        
        mock_subprocess.assert_called_once_with(["code", expected_file])
    
    @patch('subprocess.run')
    def test_create_or_open_note_existing_file(self, mock_subprocess):
        """Test opening an existing note file."""
        from core.file_operations import create_or_open_note
        
        # Create the file first
        android_dir = os.path.join(self.test_dir, "android")
        os.makedirs(android_dir)
        note_file = os.path.join(android_dir, "2025-01-15.md")
        with open(note_file, "w") as f:
            f.write("# Existing content")
        
        create_or_open_note(self.test_dir, "android", "2025-01-15", "vim")
        
        # Content should remain unchanged
        with open(note_file, "r") as f:
            content = f.read()
            self.assertEqual(content, "# Existing content")
        
        mock_subprocess.assert_called_once_with(["vim", note_file])
    
    @unittest.skipIf(pathspec is None, "pathspec not installed")
    def test_load_gitignore_patterns_no_file(self):
        """Test loading gitignore patterns when no .gitignore exists."""
        spec = load_gitignore_patterns(self.test_dir)
        self.assertFalse(spec.match_file("test.txt"))
    
    @unittest.skipIf(pathspec is None, "pathspec not installed")
    def test_load_gitignore_patterns_with_file(self):
        """Test loading gitignore patterns from .gitignore file."""
        gitignore_path = os.path.join(self.test_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("*.pyc\n__pycache__/\n")
        
        spec = load_gitignore_patterns(self.test_dir)
        self.assertTrue(spec.match_file("test.pyc"))
        self.assertTrue(spec.match_file("__pycache__/test.py"))
        self.assertFalse(spec.match_file("test.py"))

if __name__ == '__main__':
    unittest.main()
