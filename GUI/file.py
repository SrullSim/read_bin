import flet as ft
import flet_map as map
import math
from business_logic.src.reader import Reader




def main(page: ft.Page):
    page.title = " - Flight Path"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.padding = 20


    # משתנים לשמירת layers
    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    polyline_layer_ref = ft.Ref[map.PolylineLayer]()

    # משתנה לשמירת הנתונים שעובדו
    processed_data = []

    # Container למפה
    map_container = ft.Container(expand=True)

    def calculate_distance(lat1, lon1, lat2, lon2):
        """חישוב מרחק בין שתי נקודות (בקילומטרים)"""
        R = 6371  # רדיוס כדור הארץ בק"מ

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def create_map_with_route(coordinates_list):
        """יצירת מפה עם מסלול טיסה"""
        if not coordinates_list:
            return ft.Text("אין נתונים להצגה", color=ft.Colors.RED)

        # נקודת מרכז - ממוצע של כל הנקודות
        avg_lat = sum(coord["Lat"] for coord in coordinates_list) / len(coordinates_list)
        avg_lng = sum(coord["Lng"] for coord in coordinates_list) / len(coordinates_list)

        # יצירת markers עבור כל נקודה במרחק מסוים
        markers = []
        marker_distance_km = 1.5  # מרחק בין markers בק"מ

        # marker התחלה (ירוק)
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
            prev_coord = coordinates_list[i - 1]
            curr_coord = coordinates_list[i]

            distance = calculate_distance(
                prev_coord["Lat"], prev_coord["Lng"],
                curr_coord["Lat"], curr_coord["Lng"]
            )
            accumulated_distance += distance

            # הוספת marker כל X קילומטרים
            if accumulated_distance >= marker_distance_km:
                markers.append(
                    map.Marker(
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=20),
                        coordinates=map.MapLatitudeLongitude(
                            curr_coord["Lat"],
                            curr_coord["Lng"]
                        )
                    )
                )
                accumulated_distance = 0

        # marker סיום (אדום)
        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.RED, size=40),
                coordinates=map.MapLatitudeLongitude(
                    coordinates_list[-1]["Lat"],
                    coordinates_list[-1]["Lng"]
                )
            )
        )

        # יצירת קו המסלול
        route_polyline = map.PolylineMarker(
            border_stroke_width=3,
            border_color=ft.Colors.LIGHT_BLUE,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE),
            coordinates=[
                map.MapLatitudeLongitude(coord["Lat"], coord["Lng"])
                for coord in coordinates_list
            ],
        )

        # יצירת המפה
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
        """טיפול בבחירת קובץ"""
        if e.files:
            # שלב 1: קבלת הנתיב של הקובץ שנבחר
            file_path = e.files[0].path
            file_name = e.files[0].name

            # שלב 2: עדכון סטטוס שהקובץ נבחר
            status_text.value = f"קובץ נבחר: {file_name} - מעבד..."
            status_text.color = ft.Colors.BLUE
            page.update()

            try:
                # שלב 3: יצירת אובייקט Reader עם הנתיב של הקובץ שנבחר
                reader = Reader(file_path)

                # שלב 4: קריאה ועיבוד הקובץ
                processed_data = reader.read_bin_file()

                # שלב 5: בדיקה אם יש נתונים
                if processed_data and len(processed_data) > 0:
                    status_text.value = f"נמצאו {len(processed_data)} נקודות במסלול ✈️"
                    status_text.color = ft.Colors.GREEN

                    # שלב 6: יצירת המפה עם המסלול על בסיס הנתונים שעובדו
                    map_widget = create_map_with_route(processed_data)
                    map_container.content = map_widget

                else:
                    status_text.value = "לא נמצאו נקודות GPS בקובץ"
                    status_text.color = ft.Colors.ORANGE

            except Exception as ex:
                # שלב 7: טיפול בשגיאות
                status_text.value = f"שגיאה בעיבוד הקובץ: {str(ex)}"
                status_text.color = ft.Colors.RED
                print(f"Error processing file: {ex}")

            page.update()

    # יצירת file picker
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # כפתור בחירת קובץ
    upload_button = ft.ElevatedButton(
        "Upload File",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            dialog_title="Choose BIN file",
            allow_multiple=False,
            allowed_extensions=["bin"]  # רק קבצי .bin
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