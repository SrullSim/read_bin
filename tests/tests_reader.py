"""Unit tests for the Reader class and configuration settings."""

from src.utils.configurations import BIN_FILE_PATH
from src.business_logic.src.read_bin_file import ReadeBinFile


def test_bin_file_path():
    assert isinstance(BIN_FILE_PATH, str)
    assert BIN_FILE_PATH.endswith(".bin")
    print(f"Test passed: BIN_FILE_PATH is set to {BIN_FILE_PATH}")


def read_bin_file():
    reader = ReadeBinFile(BIN_FILE_PATH)
    data = reader.process_bin_file()
    pass


def run_tests():
    test_bin_file_path()
