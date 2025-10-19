import flet as ft
from business_logic.src.reader import Reader


class FileProcessor:
    """Handles file selection and data processing."""

    def __init__(self, status_text, map_builder, map_container, page):
        self.status_text = status_text
        self.map_builder = map_builder
        self.map_container = map_container
        self.page = page

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """Processes the selected file and updates the UI."""
        if e.files:
            file_path = e.files[0].path
            file_name = e.files[0].name
            self.status_text.value = f"File selected: {file_name} - processing"
            self.status_text.color = ft.Colors.BLUE
            self.page.update()
            try:
                reader = Reader(file_path)
                processed_data = reader.read_bin_file()
                if processed_data and len(processed_data) > 0:
                    self.status_text.value = f"Found {len(processed_data)} points in flight path ✈️"
                    self.status_text.color = ft.Colors.GREEN
                    map_widget = self.map_builder.create_map_with_route(processed_data, self.page)
                    self.map_container.content = map_widget
                else:
                    self.status_text.value = "No GPS found in this file"
                    self.status_text.color = ft.Colors.ORANGE
            except Exception as ex:
                self.status_text.value = f"Error processing file: {str(ex)}"
                self.status_text.color = ft.Colors.RED
                print(f"Error processing file: {ex}")
            self.page.update()