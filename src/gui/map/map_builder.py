# """build the map with layers and markers"""

import math

import flet as ft
import flet_map as map_ft

from src.utils.configurations import LATITUDE_FIELD, LONGITUDE_FIELD, MARKER_DISTANCE_KM, URL_TEMPLATE, LAUNCH_URL
from src.utils.logger_factory import logger


class MapRouteBuilder:

    def __init__(self) -> None:
        self.marker_layer_ref = ft.Ref[map_ft.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map_ft.PolylineLayer]()
        self.map_container = ft.Container(expand=True)

    def create_map_with_route(self, coordinates_list: list, page: ft.Page) -> map_ft.Map or ft.Text:
        """Builds the map widget with the flight route."""
        if not coordinates_list:
            return ft.Text("No data provided", color=ft.Colors.RED)

        try:
            start_point_lat: float = self._get_map_lat_start_point(coordinates_list)
            start_point_lng: float = self._get_map_lng_start_point(coordinates_list)

            markers_to_mark_on_the_map = self._create_flight_markers(coordinates_list)
            route_polyline = self._create_route_polyline(coordinates_list)
            map_widget = self._build_map_widget(
                start_point_lat, start_point_lng, markers_to_mark_on_the_map, route_polyline, page
            )

            logger.info(
                f"Map built with {len(coordinates_list)} coordinates and {len(markers_to_mark_on_the_map)} markers"
            )
            return map_widget

        except Exception as e:
            logger.error(f"Error building map: {str(e)}")
            return ft.Text(f"Error creating map: {str(e)}")

    def _get_map_lat_start_point(self, coordinates_list: list) -> float:
        """Returns the center coordinates for the map (using the first point)."""
        first_point = coordinates_list[0]
        return first_point[LATITUDE_FIELD]

    def _get_map_lng_start_point(self, coordinates_list: list) -> float:
        """Returns the center coordinates for the map (using the first point)."""
        first_point = coordinates_list[0]
        return first_point[LONGITUDE_FIELD]

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

    def _create_flight_markers(self, coordinates_list: list) -> list[map_ft.Marker]:
        """Creates all markers for the flight route: start, intermediate, and end markers."""
        all_markers_to_mark_on_the_map = []

        # Start marker (takeoff)
        start_marker = self._create_start_marker(coordinates_list[0])
        all_markers_to_mark_on_the_map.append(start_marker)

        # Intermediate markers (along the route)
        intermediate_markers = self._create_intermediate_markers(coordinates_list)
        all_markers_to_mark_on_the_map.extend(intermediate_markers)

        # End marker (landing)
        end_marker = self._create_end_marker(coordinates_list[-1])
        all_markers_to_mark_on_the_map.append(end_marker)

        return all_markers_to_mark_on_the_map

    def _create_start_marker(self, coordinate: dict) -> map_ft.Marker:
        """Creates the takeoff marker (green plane icon)."""
        return map_ft.Marker(
            content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=30),
            coordinates=map_ft.MapLatitudeLongitude(
                coordinate[LATITUDE_FIELD],
                coordinate[LONGITUDE_FIELD],
            ),
        )

    def _create_end_marker(self, coordinate: dict) -> map_ft.Marker:
        """Creates the landing marker (red plane icon)."""
        return map_ft.Marker(
            content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
            coordinates=map_ft.MapLatitudeLongitude(
                coordinate[LATITUDE_FIELD],
                coordinate[LONGITUDE_FIELD],
            ),
        )

    def _create_intermediate_markers(self, coordinates_list: list) -> list[map_ft.Marker]:
        """Creates markers along the route at specified distance intervals."""
        roads_marks: list = []
        accumulated_distance: int = 0
        marker_distance_km: int = MARKER_DISTANCE_KM

        for i in range(1, len(coordinates_list)):
            prev_point: dict = coordinates_list[i - 1]
            current_point: dict = coordinates_list[i]

            segment_distance: float = self.calculate_distance(
                prev_point[LATITUDE_FIELD],
                prev_point[LONGITUDE_FIELD],
                current_point[LATITUDE_FIELD],
                current_point[LONGITUDE_FIELD],
            )

            accumulated_distance += segment_distance

            if accumulated_distance >= marker_distance_km:
                location_mark = self._create_waypoint_marker(current_point)
                roads_marks.append(location_mark)
                accumulated_distance = 0

        return roads_marks

    def _create_waypoint_marker(self, coordinate: dict) -> map_ft.Marker:
        """Creates a single waypoint marker (black location pin)."""
        return map_ft.Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLACK87, size=15),
            coordinates=map_ft.MapLatitudeLongitude(
                coordinate[LATITUDE_FIELD],
                coordinate[LONGITUDE_FIELD],
            ),
        )

    def _create_route_polyline(self, coordinates_list: list) -> map_ft.PolylineMarker:
        """Creates the polyline that draws the flight path on the map."""
        return map_ft.PolylineMarker(
            border_stroke_width=5,
            border_color=ft.Colors.OUTLINE,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
            coordinates=[
                map_ft.MapLatitudeLongitude(coord[LATITUDE_FIELD], coord[LONGITUDE_FIELD]) for coord in coordinates_list
            ],
        )

    def _build_map_widget(
        self,
        center_lat: float,
        center_lng: float,
        markers: list[map_ft.Marker],
        route_polyline: map_ft.PolylineMarker,
        page: ft.Page,
    ) -> map_ft.Map:
        """Constructs the complete map widget with all layers and configurations."""
        tile_layer = self._create_tile_layer()
        attribution_layer = self._create_attribution_layer(page)
        polyline_layer = self._create_polyline_layer(route_polyline)
        marker_layer = self._create_marker_layer(markers)

        return map_ft.Map(
            expand=True,
            initial_center=map_ft.MapLatitudeLongitude(center_lat, center_lng),
            initial_zoom=10,
            interaction_configuration=map_ft.MapInteractionConfiguration(flags=map_ft.MapInteractiveFlag.ALL),
            on_init=lambda e: print("Initialized Map"),
            layers=[tile_layer, attribution_layer, polyline_layer, marker_layer],
        )

    def _create_tile_layer(self) -> map_ft.TileLayer:
        """Creates the base map tile layer (OpenStreetMap)."""
        return map_ft.TileLayer(
            url_template=URL_TEMPLATE,
            on_image_error=lambda e: print("TileLayer Error"),
        )

    def _create_attribution_layer(self, page: ft.Page) -> map_ft.RichAttribution:
        """Creates the attribution layer with credits to OpenStreetMap and Flet."""
        return map_ft.RichAttribution(
            attributions=[
                map_ft.TextSourceAttribution(
                    text="OpenStreetMap Contributors",
                    on_click=lambda e: page.launch_url(LAUNCH_URL),
                ),
                map_ft.TextSourceAttribution(
                    text="Flet",
                    on_click=lambda e: page.launch_url("https://flet.dev"),
                ),
            ]
        )

    def _create_polyline_layer(self, route_polyline: map_ft.PolylineMarker) -> map_ft.PolylineLayer:
        """Creates the layer that contains the flight route polyline."""
        return map_ft.PolylineLayer(
            ref=self.polyline_layer_ref,
            polylines=[route_polyline],
        )

    def _create_marker_layer(self, markers: list[map_ft.Marker]) -> map_ft.MarkerLayer:
        """Creates the layer that contains all markers (start, waypoints, end)."""
        return map_ft.MarkerLayer(
            ref=self.marker_layer_ref,
            markers=markers,
        )
