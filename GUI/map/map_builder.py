import flet as ft
import flet_map as map
import math


class MapRouteBuilder:
    """Builds map widgets and visualizes flight routes."""

    def __init__(self):
        self.marker_layer_ref = ft.Ref[map.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map.PolylineLayer]()
        self.map_container = ft.Container(expand=True)

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate the distance between two lat/lon points in kilometers."""
        world_radius = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return world_radius * c

    def create_map_with_route(self, coordinates_list, page):
        """ Builds the map widget with the flight route."""
        if not coordinates_list:
            return ft.Text("No data provided", color=ft.Colors.RED)

        avg_lat = sum(coord["Lat"] for coord in coordinates_list) / len(coordinates_list)
        avg_lng = sum(coord["Lng"] for coord in coordinates_list) / len(coordinates_list)

        markers = []
        marker_distance_km = 1.5

        # Start marker
        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=30),
                coordinates=map.MapLatitudeLongitude(
                    coordinates_list[0]["Lat"],
                    coordinates_list[0]["Lng"]
                )
            )
        )

        accumulated_distance = 0
        for i in range(1, len(coordinates_list)):
            prev_point = coordinates_list[i - 1]
            current_point = coordinates_list[i]
            distance = self.calculate_distance(
                prev_point["Lat"], prev_point["Lng"],
                current_point["Lat"], current_point["Lng"]
            )
            accumulated_distance += distance
            if accumulated_distance >= marker_distance_km:
                markers.append(
                    map.Marker(
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLACK87, size=15),
                        coordinates=map.MapLatitudeLongitude(
                            current_point["Lat"],
                            current_point["Lng"]
                        )
                    )
                )
                accumulated_distance = 0

        # End marker
        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
                coordinates=map.MapLatitudeLongitude(
                    coordinates_list[-1]["Lat"],
                    coordinates_list[-1]["Lng"]
                )
            )
        )

        route_polyline = map.PolylineMarker(
            border_stroke_width=5,
            border_color=ft.Colors.OUTLINE,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
            coordinates=[
                map.MapLatitudeLongitude(coord["Lat"], coord["Lng"])
                for coord in coordinates_list
            ],
        )

        map_widget = map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(avg_lat, avg_lng),
            initial_zoom=8,
            interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.ALL
            ),
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
                            on_click=lambda e: page.launch_url(
                                "https://openstreetmap.org/copyright"
                            ),
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
        return map_widget
