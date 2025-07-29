import unittest
import tempfile
import os
from unittest.mock import patch
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.config import TILConfig, load_tilrc_config

class TestTILConfig(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_empty_config(self):
        """Test loading config when no .tilrc exists."""
        config = TILConfig(self.test_dir)
        self.assertEqual(config.default_editor, "code")
        self.assertIsNone(config.default_category)
        self.assertIsNone(config.default_link_tag)
        self.assertFalse(config.open_browser)
    
    def test_load_config_from_current_dir(self):
        """Test loading config from current directory."""
        tilrc_path = os.path.join(self.test_dir, ".tilrc")
        with open(tilrc_path, "w") as f:
            f.write("""[general]
default_editor = vim
default_category = test
default_link_tag = awesome
open_browser = true
""")
        
        config = TILConfig(self.test_dir)
        self.assertEqual(config.default_editor, "vim")
        self.assertEqual(config.default_category, "test")
        self.assertEqual(config.default_link_tag, "awesome")
        self.assertTrue(config.open_browser)
    
    @patch('os.path.expanduser')
    def test_load_config_from_home(self, mock_expanduser):
        """Test loading config from home directory."""
        home_dir = tempfile.mkdtemp()
        mock_expanduser.return_value = os.path.join(home_dir, ".tilrc")
        
        tilrc_path = os.path.join(home_dir, ".tilrc")
        with open(tilrc_path, "w") as f:
            f.write("""[general]
default_editor = nano
""")
        
        config = load_tilrc_config(self.test_dir)
        self.assertEqual(config.get("general", "default_editor", fallback="code"), "nano")

if __name__ == '__main__':
    unittest.main()
