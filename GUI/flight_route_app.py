import flet as ft
from GUI.map.map_builder import MapRouteBuilder
from GUI.file_handler.file_processor import FileProcessor


class FlightRouteApp:
    """Main application class for the flight route viewer."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = " - Flight Path"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.rtl = True
        self.page.padding = 20

        self.map_builder = MapRouteBuilder()
        self.status_text = ft.Text(
            "Please choose file",
            size=16,
            weight=ft.FontWeight.BOLD
        )
        self.file_processor = FileProcessor(
            self.status_text,
            self.map_builder,
            self.map_builder.map_container,
            self.page
        )

        self.file_picker = ft.FilePicker(on_result=self.file_processor.on_file_picked)
        self.page.overlay.append(self.file_picker)

        self.upload_button = ft.ElevatedButton(
            "Upload File",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: self.file_picker.pick_files(
                dialog_title="Choose BIN file",
                allow_multiple=False,
                allowed_extensions=["bin"]
            ),
        )

    def build(self):
        """Builds the main UI layout."""
        self.page.add(
            ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "✈ Flight route app ✈",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Divider(),
                        self.upload_button,
                        self.status_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                ),
                self.map_builder.map_container,
            ], expand=True, spacing=10)
        )