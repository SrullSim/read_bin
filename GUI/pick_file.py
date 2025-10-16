import flet as ft
import flet_map as map


def on_file_picked(e: ft.FilePickerResultEvent):
    """choose file and process it"""
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