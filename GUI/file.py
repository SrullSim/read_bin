import flet as ft
import flet_map as map
import math
from business_logic.src.reader import Reader




def main(page: ft.Page):
    page.title = " - Flight Path"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.padding = 20


    # define layers
    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    polyline_layer_ref = ft.Ref[map.PolylineLayer]()

    # Container למפה
    map_container = ft.Container(expand=True)

    def calculate_distance(lat1, lon1, lat2, lon2):
        """ calculate the distance between two lat/lon points in kilometers """
        world_radius = 6371  # Radius of the Earth

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return world_radius * c

    def create_map_with_route(coordinates_list):
        """ build map with route based on coordinates_list """
        if not coordinates_list:
            return ft.Text(" no data provide ", color=ft.Colors.RED)

        # average of all lat/lng points in the coordinates_list
        avg_lat = sum(coord["Lat"] for coord in coordinates_list) / len(coordinates_list)
        avg_lng = sum(coord["Lng"] for coord in coordinates_list) / len(coordinates_list)

        # list of marks to put on the map
        markers = []
        marker_distance_km = 0.3  # distance between markers in kilometers

        # marker of start point (green)
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

            distance = calculate_distance(
                prev_point["Lat"], prev_point["Lng"],
                current_point["Lat"], current_point["Lng"]
            )
            accumulated_distance += distance

            # mark every marker_distance_km kilometers
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

        # marker of end point (red)
        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
                coordinates=map.MapLatitudeLongitude(
                    coordinates_list[-1]["Lat"],
                    coordinates_list[-1]["Lng"]
                )
            )
        )

        # create polyline for the path
        route_polyline = map.PolylineMarker(
            border_stroke_width=5,
            border_color=ft.Colors.OUTLINE,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
            coordinates=[
                map.MapLatitudeLongitude(coord["Lat"], coord["Lng"])
                for coord in coordinates_list
            ],
        )

        # build the map
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
                    ref=polyline_layer_ref,
                    polylines=[route_polyline],
                ),
                map.MarkerLayer(
                    ref=marker_layer_ref,
                    markers=markers,
                ),
            ],
        )

        return map_widget

    def on_file_picked(e: ft.FilePickerResultEvent):
        """choose file and process it"""
        if e.files:
            # get the path of the selected file
            file_path = e.files[0].path
            file_name = e.files[0].name

            # file selected status update
            status_text.value = f"file selected : {file_name} - processing"
            status_text.color = ft.Colors.BLUE
            page.update()

            try:
                # build the reader to process the data
                reader = Reader(file_path)

                # read and process the data from the file
                processed_data = reader.read_bin_file()

                #
                if processed_data and len(processed_data) > 0:
                    status_text.value = f"found {len(processed_data)} points in flight path ✈️"
                    status_text.color = ft.Colors.GREEN

                    # build the map and path according the processed data
                    map_widget = create_map_with_route(processed_data)
                    map_container.content = map_widget

                else:
                    status_text.value = "no GPS found in this file"
                    status_text.color = ft.Colors.ORANGE

            except Exception as ex:
                # error handling
                status_text.value = f"שגיאה בעיבוד הקובץ: {str(ex)}"
                status_text.color = ft.Colors.RED
                print(f"Error processing file: {ex}")

            page.update()

    # create file picker
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # file upload button
    upload_button = ft.ElevatedButton(
        "Upload File",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            dialog_title="Choose BIN file",
            allow_multiple=False,
            allowed_extensions=["bin"]  # check thet only .bin files upload
        ),
    )

    status_text = ft.Text(
        "please choose file",
        size=16,
        weight=ft.FontWeight.BOLD
    )

    # פריסה
    page.add(
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
                    upload_button,
                    status_text,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
            ),
            map_container,
        ], expand=True, spacing=10)
    )


ft.app(target=main)