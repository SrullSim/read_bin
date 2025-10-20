import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
# DATA_DIR = PROJECT_ROOT / "data"
UI_DIR = PROJECT_ROOT / "gui"
CONFIG_DIR = PROJECT_ROOT / "config"
FILES_HANDLER_DIR = UI_DIR / "file_handler"


FORMATTER = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d, %H:%M")
LOG_FILE = "project_logs.txt"  # The name of the log file.


MARKER_DISTANCE_KM = 200  # Default distance between markers in kilometers
MSG_NUMBER_TO_SHOW = 5000  # Default distance between massag markers in kilometers
# names of latitude and longitude fields in the data
LATITUDE_FIELD = "Lat"
LONGITUDE_FIELD = "Lng"


SETTINGS_FILE_PATH = CONFIG_DIR / "settings.json"
try:
    with open(SETTINGS_FILE_PATH, "r") as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
    print(f"WARNING: Configuration file not found at {SETTINGS_FILE_PATH}. Using defaults.")


BIN_FILE_PATH = settings.get("BIN_FILE_PATH", "C:\\Users\\User\\OneDrive\\Desktop\\step.0\\log_file_test_01.bin")
