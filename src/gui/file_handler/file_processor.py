import traceback
from typing import Callable

import flet as ft

from src.utils.logger_factory import logger
from src.business_logic.src.read_bin_file import ReadeBinFile
from src.gui.map.map_builder import MapRouteBuilder



class FileProcessor:
    """Handles file selection and data processing."""

    def __init__(
        self, status_text: ft.Text, map_builder: MapRouteBuilder, map_container: Callable, page: ft.Page
    ):  # TODO use Callable for functions ✅

        self.status_text = status_text
        self.map_builder = map_builder
        self.map_container = map_container
        self.page = page

    def on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        """Processes the selected file and updates the UI."""
        if not e.files:
            return None

        file_path: str = e.files[0].path  # TODO need typing ✅
        file_name: str = e.files[0].name

        self.update_status_after_selected_file(file_name, ft.Colors.BLUE)

        try:
            reade_bin_file = ReadeBinFile(file_path)  # TODO the name is not clear ✅
            processed_data = reade_bin_file.process_bin_file()

            if (
                not processed_data and len(processed_data) <= 0
            ):  # TODO when we use "if not" the code is more readable ✅

                self.update_status_if_not_gps_found(ft.Colors.ORANGE)
            else:

                self.update_status_if_gps_found(len(processed_data), ft.Colors.GREEN)

                map_widget = self.map_builder.create_map_with_route(processed_data, self.page)
                self.map_container.content = map_widget

        except Exception as ex:
            self.update_status_when_failed_to_process_file(ex, ft.Colors.RED)
            traceback.print_exc()
            logger.error(f"Error processing file: {ex}")

        self.page.update()

    def update_status_after_selected_file(self, file_name: str, color: ft.Colors) -> None:
        """Update the status text in the UI"""
        self.status_text.value = f"File selected: {file_name} - processing"
        self.status_text.color = color
        self.page.update()

    def update_status_if_not_gps_found(self, color: ft.Colors) -> None:
        """Update the status text in the UI if file don't have any GPS coordinates ."""
        self.status_text.value = "No GPS found in this file"
        self.status_text.color = color
        self.page.update()

    def update_status_if_gps_found(self, num_points: int, color: ft.Colors) -> None:
        """Update the status text in the UI if file have GPS coordinates ."""
        self.status_text.value = f"Found {num_points} points in flight path ✈️"
        self.status_text.color = color
        self.page.update()

    def update_status_when_failed_to_process_file(self, ex: Exception, color: ft.Colors) -> None:
        """General method to update the status text in the UI."""

        self.status_text.value = f"Error processing file: {str(ex)}"
        self.status_text.color = color
        self.page.update()
