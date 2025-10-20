"""Unit tests for the Reader class and configuration settings."""

from config.configurations import BIN_FILE_PATH
from src.business_logic.src.reader import Reader


def test_bin_file_path():
    assert isinstance(BIN_FILE_PATH, str)
    assert BIN_FILE_PATH.endswith(".bin")
    print(f"Test passed: BIN_FILE_PATH is set to {BIN_FILE_PATH}")


def read_bin_file():
    reader = Reader(BIN_FILE_PATH)
    data = reader.read_bin_file()
    pass


def run_tests():
    test_bin_file_path()
