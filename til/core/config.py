import os
from configparser import ConfigParser

def load_tilrc_config(base_dir: str):
    """Load configuration from .tilrc files."""
    config = ConfigParser()

    # 우선순위: 현재 디렉토리 > 홈 디렉토리
    possible_paths = [
        os.path.join(base_dir, ".tilrc"),
        os.path.expanduser("~/.tilrc")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            config.read(path)
            print(f"⚙️  Loaded settings from {path}")
            return config

    return config  # 빈 ConfigParser

class TILConfig:
    """TIL configuration manager."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.config = load_tilrc_config(base_dir)
    
    @property
    def default_editor(self) -> str:
        return self.config.get("general", "default_editor", fallback="code")
    
    @property
    def default_category(self) -> str:
        return self.config.get("general", "default_category", fallback=None)
    
    @property
    def default_link_tag(self) -> str:
        return self.config.get("general", "default_link_tag", fallback=None)
    
    @property
    def open_browser(self) -> bool:
        return self.config.getboolean("general", "open_browser", fallback=False)
