import flet as ft
import flet_map as map
import math
from GUI.flight_route_app import FlightRouteApp
from business_logic.src.reader import Reader






def main(page: ft.Page):
    """Entry point for the Flet app."""
    app = FlightRouteApp(page)
    app.build()

ft.app(target=main)