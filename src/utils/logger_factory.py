"""This module defines a LoggerFactory class that creates and configures logs instances."""

import logging
import sys
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

from src.utils.configurations import FORMATTER, LOG_FILE

# Define the format for the log messages.
# This format includes the timestamp, log level, and the message itself.
# Timestamp format: YYYY-MM-DD, HH:MM


class LoggerFactory:
    """
    A factory class to create and configure logs instances.
    """

    def get_console_handler(self) -> logging.StreamHandler:
        """
        Creates a handler to print log messages to the console (command line).
        """
        # This handler will output to standard out (the console).
        console_handler = logging.StreamHandler(sys.stdout)
        # Set the formatter for this handler.
        console_handler.setFormatter(FORMATTER)
        return console_handler

    def get_file_handler(self) -> TimedRotatingFileHandler:
        """
        Creates a handler to write log messages to a file.
        """
        file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7, encoding="utf-8")
        file_handler.setFormatter(FORMATTER)
        return file_handler

    def get_logger(self, logger_name: str) -> Logger:
        """
        Creates and configures a logs instance.
        """
        # Get a logs instance with the specified name.
        logger = logging.getLogger(logger_name)

        # Set the logging level. INFO means it will handle INFO, WARNING, ERROR, and CRITICAL messages.
        logger.setLevel(logging.INFO)

        # Add the console and file handlers to the logs.
        # This logs will now log to both the console and the file.
        logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())

        # This sent log messages to the root logs.
        logger.propagate = True

        return logger


# create a global logs instance for singleton usage
logger = LoggerFactory().get_logger(__name__)


if __name__ == "__main__":
    # Get the logs instance. You can name it anything.
    # It's common practice to use __name__ to get the name of the current module.
    pass
