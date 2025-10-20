"""build the map with layers and markers"""

import math

import flet as ft
import flet_map as map_ft

from config.configurations import LATITUDE_FIELD, LONGITUDE_FIELD, MARKER_DISTANCE_KM
from logs.logger_factory import logger


class MapRouteBuilder:
    """Builds map widgets and visualizes flight routes."""

    def __init__(self) -> None:
        self.marker_layer_ref = ft.Ref[map_ft.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map_ft.PolylineLayer]()
        self.map_container = ft.Container(expand=True)
        self.logger = logger.get_logger(__name__)

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the distance between two lat/lon points in kilometers."""
        world_radius = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return world_radius * c

    def create_map_with_route(self, coordinates_list: list, page: ft.Page) -> ft.Control:
        """Builds the map widget with the flight route."""
        if not coordinates_list:
            return ft.Text("No data provided", color=ft.Colors.RED)

        try:

            avg_lat = coordinates_list[0][LATITUDE_FIELD]
            avg_lng = coordinates_list[0][LONGITUDE_FIELD]

            markers = []
            marker_distance_km = MARKER_DISTANCE_KM

            # Start marker
            markers.append(
                map_ft.Marker(
                    content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=30),
                    coordinates=map_ft.MapLatitudeLongitude(
                        coordinates_list[0][LATITUDE_FIELD],
                        coordinates_list[0][LONGITUDE_FIELD],
                    ),
                )
            )

            accumulated_distance = 0
            for i in range(1, len(coordinates_list)):
                prev_point = coordinates_list[i - 1]
                current_point = coordinates_list[i]
                distance = self.calculate_distance(
                    prev_point[LATITUDE_FIELD],
                    prev_point[LONGITUDE_FIELD],
                    current_point[LATITUDE_FIELD],
                    current_point[LONGITUDE_FIELD],
                )
                accumulated_distance += distance
                if accumulated_distance >= marker_distance_km:
                    markers.append(
                        map_ft.Marker(
                            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLACK87, size=15),
                            coordinates=map_ft.MapLatitudeLongitude(
                                current_point[LATITUDE_FIELD],
                                current_point[LONGITUDE_FIELD],
                            ),
                        )
                    )
                    accumulated_distance = 0

            # End marker
            markers.append(
                map_ft.Marker(
                    content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
                    coordinates=map_ft.MapLatitudeLongitude(
                        coordinates_list[-1][LATITUDE_FIELD],
                        coordinates_list[-1][LONGITUDE_FIELD],
                    ),
                )
            )

            route_polyline = map_ft.PolylineMarker(
                border_stroke_width=5,
                border_color=ft.Colors.OUTLINE,
                color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
                coordinates=[
                    map_ft.MapLatitudeLongitude(coord[LATITUDE_FIELD], coord[LONGITUDE_FIELD])
                    for coord in coordinates_list
                ],
            )

            map_widget = map_ft.Map(
                expand=True,
                initial_center=map_ft.MapLatitudeLongitude(avg_lat, avg_lng),
                initial_zoom=10,
                interaction_configuration=map_ft.MapInteractionConfiguration(flags=map_ft.MapInteractiveFlag.ALL),
                on_init=lambda e: print("Initialized Map"),
                layers=[
                    map_ft.TileLayer(
                        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        on_image_error=lambda e: print("TileLayer Error"),
                    ),
                    map_ft.RichAttribution(
                        attributions=[
                            map_ft.TextSourceAttribution(
                                text="OpenStreetMap Contributors",
                                on_click=lambda e: page.launch_url("https://openstreetmap.org/copyright"),
                            ),
                            map_ft.TextSourceAttribution(
                                text="Flet",
                                on_click=lambda e: page.launch_url("https://flet.dev"),
                            ),
                        ]
                    ),
                    map_ft.PolylineLayer(
                        ref=self.polyline_layer_ref,
                        polylines=[route_polyline],
                    ),
                    map_ft.MarkerLayer(
                        ref=self.marker_layer_ref,
                        markers=markers,
                    ),
                ],
            )
            self.logger.info(f"Map built with {len(coordinates_list)} coordinates and {len(markers)} markers")
            return map_widget

        except Exception as e:
            self.logger.error(f"Error building map: {str(e)}")
            return ft.Text(
                f"Error creating map: {str(e)}",
            )
