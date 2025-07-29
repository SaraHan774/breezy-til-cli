import unittest
import tempfile
import os
import sys
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.zip_generator import generate_til_zip, generate_current_month_zip

class TestZipGenerator(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self._create_test_files()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """Create test TIL files."""
        # Create android category
        android_dir = os.path.join(self.test_dir, "android")
        os.makedirs(android_dir)
        
        # Create test files
        files = [
            ("android/2025-01-10.md", "# TIL - 2025-01-10\n\nAndroid content"),
            ("android/2025-01-15.md", "# TIL - 2025-01-15\n\nMore Android content"),
            ("python/2025-01-12.md", "# TIL - 2025-01-12\n\nPython content"),
        ]
        
        for filepath, content in files:
            full_path = os.path.join(self.test_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    def test_generate_til_zip_date_range(self):
        """Test generating ZIP for date range."""
        generate_til_zip(self.test_dir, "2025-01-10", "2025-01-12")
        
        zip_file = os.path.join(self.test_dir, "zip-2025-01-10_to_2025-01-12.md")
        self.assertTrue(os.path.exists(zip_file))
        
        with open(zip_file, "r") as f:
            content = f.read()
            self.assertIn("# 📦 TIL ZIP: 2025-01-10 → 2025-01-12", content)
            self.assertIn("## 📁 android / 2025-01-10", content)
            self.assertIn("## 📁 python / 2025-01-12", content)
            self.assertIn("Android content", content)
            self.assertIn("Python content", content)
            # Should not include 2025-01-15 (outside range)
            self.assertNotIn("2025-01-15", content)
    
    def test_generate_til_zip_no_files_in_range(self):
        """Test generating ZIP when no files in date range."""
        # This should not create a file and should print a message
        generate_til_zip(self.test_dir, "2025-02-01", "2025-02-28")
        
        zip_file = os.path.join(self.test_dir, "zip-2025-02-01_to_2025-02-28.md")
        self.assertFalse(os.path.exists(zip_file))
    
    def test_generate_current_month_zip(self):
        """Test generating ZIP for current month."""
        from datetime import datetime
        
        # Mock current date to January 2025
        with patch('core.zip_generator.datetime') as mock_date:
            mock_date.today.return_value = datetime(2025, 1, 20)
            mock_date.strptime = datetime.strptime  # Keep strptime working
            
            generate_current_month_zip(self.test_dir)
        
        zip_file = os.path.join(self.test_dir, "zip-2025-01.md")
        self.assertTrue(os.path.exists(zip_file))
        
        with open(zip_file, "r") as f:
            content = f.read()
            self.assertIn("# 📦 TIL ZIP: 2025-01", content)
            self.assertIn("Android content", content)
            self.assertIn("Python content", content)

if __name__ == '__main__':
    unittest.main()
