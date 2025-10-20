import math

import flet as ft
import flet_map as map

from config.config import LATITUDE_FIELD, LONGITUDE_FIELD, MARKER_DISTANCE_KM
from logger.logger import LoggerFactory

# build the map with layers and markers


class MapRouteBuilder:
    """Builds map widgets and visualizes flight routes."""

    def __init__(self):
        self.marker_layer_ref = ft.Ref[map.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map.PolylineLayer]()
        self.map_container = ft.Container(expand=True)
        self.logger = LoggerFactory().get_logger(__name__)

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2) -> float:
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

    def create_map_with_route(self, coordinates_list, page) -> ft.Control:
        """Builds the map widget with the flight route."""
        if not coordinates_list:
            return ft.Text("No data provided", color=ft.Colors.RED)

        try:

            avg_lat = sum(coord[LATITUDE_FIELD] for coord in coordinates_list) / len(coordinates_list)
            avg_lng = sum(coord[LONGITUDE_FIELD] for coord in coordinates_list) / len(coordinates_list)

            markers = []
            marker_distance_km = MARKER_DISTANCE_KM

            # Start marker
            markers.append(
                map.Marker(
                    content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=30),
                    coordinates=map.MapLatitudeLongitude(
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
                        map.Marker(
                            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLACK87, size=15),
                            coordinates=map.MapLatitudeLongitude(
                                current_point[LATITUDE_FIELD],
                                current_point[LONGITUDE_FIELD],
                            ),
                        )
                    )
                    accumulated_distance = 0

            # End marker
            markers.append(
                map.Marker(
                    content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
                    coordinates=map.MapLatitudeLongitude(
                        coordinates_list[-1][LATITUDE_FIELD],
                        coordinates_list[-1][LONGITUDE_FIELD],
                    ),
                )
            )

            route_polyline = map.PolylineMarker(
                border_stroke_width=5,
                border_color=ft.Colors.OUTLINE,
                color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
                coordinates=[
                    map.MapLatitudeLongitude(coord[LATITUDE_FIELD], coord[LONGITUDE_FIELD])
                    for coord in coordinates_list
                ],
            )

            map_widget = map.Map(
                expand=True,
                initial_center=map.MapLatitudeLongitude(avg_lat, avg_lng),
                initial_zoom=8,
                interaction_configuration=map.MapInteractionConfiguration(flags=map.MapInteractiveFlag.ALL),
                on_init=lambda e: print("Initialized Map"),
                layers=[
                    map.TileLayer(
                        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        on_image_error=lambda e: print("TileLayer Error"),
                    ),
                    map.RichAttribution(
                        attributions=[
                            map.TextSourceAttribution(
                                text="OpenStreetMap Contributors",
                                on_click=lambda e: page.launch_url("https://openstreetmap.org/copyright"),
                            ),
                            map.TextSourceAttribution(
                                text="Flet",
                                on_click=lambda e: page.launch_url("https://flet.dev"),
                            ),
                        ]
                    ),
                    map.PolylineLayer(
                        ref=self.polyline_layer_ref,
                        polylines=[route_polyline],
                    ),
                    map.MarkerLayer(
                        ref=self.marker_layer_ref,
                        markers=markers,
                    ),
                ],
            )
            # self.logger.info(f"Map built with {len(coordinates_list)} coordinates and {len(markers)} markers")
            return map_widget

        except Exception as e:
            self.logger.error(f"Error building map: {str(e)}", exception=e)
            return ft.Text(
                f"Error creating map: {str(e)}",
            )
