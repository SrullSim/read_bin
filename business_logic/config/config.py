import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
# DATA_DIR = PROJECT_ROOT / "data"
APP_DIR = PROJECT_ROOT / "src"
CONFIG_DIR = PROJECT_ROOT / "config"





SETTINGS_FILE_PATH = CONFIG_DIR / "settings.json"
try:
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
    print(f"WARNING: Configuration file not found at {SETTINGS_FILE_PATH}. Using defaults.")


BIN_FILE_PATH = settings.get("BIN_FILE_PATH", "C:\\Users\\User\\OneDrive\\Desktop\\step.0\\log_file_test_01.bin")
