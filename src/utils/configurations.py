import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SRC_DIR = PROJECT_ROOT / "src"
GUI_DIR = SRC_DIR / "gui"
FILES_HANDLER_DIR = GUI_DIR / "file_handler"
MAP_DIR = GUI_DIR / "map"
LOGS_DIR = PROJECT_ROOT / "logs"


FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s")
LOG_FILE = LOGS_DIR / "project_logs.txt"  # The name and location of the log file.


MARKER_DISTANCE_KM = 200  # Default distance between markers in kilometers
MSG_NUMBER_TO_SHOW = 10000  # Default distance between massage markers in kilometers
# names of latitude and longitude fields in the data
LATITUDE_FIELD = "Lat"
LONGITUDE_FIELD = "Lng"

PAGE_TITLE = " - Flight Path - "

URL_TEMPLATE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
LAUNCH_URL = "https://openstreetmap.org/copyright"

SETTINGS_FILE_PATH = CONFIG_DIR / "config.json"
try:
    with open(SETTINGS_FILE_PATH, "r") as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
    print(f"WARNING: Configuration file not found at {SETTINGS_FILE_PATH}. Using defaults.")


BIN_FILE_PATH = settings.get("BIN_FILE_PATH", "C:\\Users\\User\\OneDrive\\Desktop\\step.0\\log_file_test_01.bin")
