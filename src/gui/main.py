import flet as ft

from src.gui.flight_route_app import FlightRouteApp

# run the Flet app


def main(page: ft.Page) -> None:
    """Entry point for the Flet app."""
    app = FlightRouteApp(page)
    app.build()


ft.app(target=main)
