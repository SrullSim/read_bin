import flet as ft
import flet_map as map
import math


def main(page: ft.Page):
    page.title = "מסלול טיסה - Flight Path"
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
        marker_distance_km = 50  # מרחק בין markers בק"מ

        # marker התחלה (ירוק)
        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=40),
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
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=30),
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
            border_stroke_width=4,
            border_color=ft.Colors.BLUE,
            color=ft.Colors.with_opacity(0.7, ft.Colors.BLUE),
            coordinates=[
                map.MapLatitudeLongitude(coord["Lat"], coord["Lng"])
                for coord in coordinates_list
            ],
        )

        # יצירת המפה
        map_widget = map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(avg_lat, avg_lng),
            initial_zoom=6,
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
            file_path = e.files[0].path
            status_text.value = f"קובץ נבחר: {e.files[0].name}"
            status_text.color = ft.Colors.BLUE
            page.update()

            # ==========================================
            # כאן תכניס את הפונקציה שלך לעיבוד הקובץ
            # ==========================================
            # דוגמה:
            # processed_data = your_processing_function(file_path)
            #
            # הפונקציה שלך צריכה להחזיר list של dictionaries בפורמט:
            # [{"Lat": 34.555, "Lng": 23.555}, {"Lat": 35.123, "Lng": 24.789}, ...]

            # לצורך הדגמה - נתונים לדוגמה (מסלול טיסה מתל אביב לאילת)
            processed_data = [
                {"Lat": 32.0853, "Lng": 34.7818},  # תל אביב
                {"Lat": 31.8969, "Lng": 34.8186},
                {"Lat": 31.7069, "Lng": 35.0053},
                {"Lat": 31.5167, "Lng": 35.1000},
                {"Lat": 31.3264, "Lng": 35.2281},
                {"Lat": 31.0461, "Lng": 35.3728},
                {"Lat": 30.6114, "Lng": 35.0753},
                {"Lat": 30.2653, "Lng": 35.0314},
                {"Lat": 29.5581, "Lng": 34.9482},  # אילת
            ]
            # ==========================================

            if processed_data:
                status_text.value = f"נמצאו {len(processed_data)} נקודות במסלול ✈️"
                status_text.color = ft.Colors.GREEN

                # יצירת המפה עם המסלול
                map_widget = create_map_with_route(processed_data)
                map_container.content = map_widget

            else:
                status_text.value = "שגיאה בעיבוד הקובץ"
                status_text.color = ft.Colors.RED

            page.update()

    # יצירת file picker
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # כפתור בחירת קובץ
    upload_button = ft.ElevatedButton(
        "בחר קובץ להעלאה",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            dialog_title="בחר קובץ",
            allow_multiple=False
        ),
    )

    # טקסט סטטוס
    status_text = ft.Text(
        "לא נבחר קובץ",
        size=16,
        weight=ft.FontWeight.BOLD
    )

    # פריסה
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "✈️ אפליקציית מסלול טיסה ✈️",
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