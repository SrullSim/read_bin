"""Main module to run the Flight Route Flet application."""

import flet as ft

from src.gui.flight_route_app import FlightRouteApp


def main(page: ft.Page) -> None:
    """Entry point for the Flet app."""
    app = FlightRouteApp(page)
    app.build()


ft.app(target=main)
