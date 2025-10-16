import csv
from typing import Any
from pymavlink import mavutil

import csv
from typing import Any
from pymavlink import mavutil


class Reader:

    def __init__(self, path):
        self.path = path
        try:
            self.mavlink_connection = mavutil.mavlink_connection(
                self.path,
                robust_parsing=True
            )
        except Exception as e:
            print(f"error connect mavlink: {e}")
            self.mavlink_connection = None

    def read_bin_file(self, msg_number_to_show=100) -> list:
        """ get path to .bin file
        :return list of dictionaries for each flight """

        if self.mavlink_connection is None:
            print("No mavlink connection available")
            return []

        try:
            lat_lng_list = []
            previous_point = None
            msg_count = 0

            # לולאה שקוראת את כל ההודעות מהקובץ
            while True:
                # קריאת הודעה מסוג GPS
                msg = self.mavlink_connection.recv_match(
                    type=['GPS', 'GPS_RAW_INT', 'GLOBAL_POSITION_INT'],
                    blocking=False
                )

                # אם אין יותר הודעות - צא מהלולאה
                if msg is None:
                    print(f'Finished reading. Total points: {len(lat_lng_list)}')
                    break

                # בדיקה שיש את השדות הנדרשים
                if not hasattr(msg, 'Lat') or not hasattr(msg, 'Lng'):
                    continue

                # בדיקת תנאי I == 1 (אם השדה קיים)
                if hasattr(msg, 'I'):
                    if getattr(msg, 'I') != 1:
                        continue

                # קבלת הערכים האמיתיים (לא boolean)
                lat = getattr(msg, 'Lat')
                lng = getattr(msg, 'Lng')

                # המרה למעלות (לפעמים הערכים מגיעים ב-microdegrees)
                # אם הערכים גדולים מדי, חלק ב-10,000,000
                if abs(lat) > 180:
                    lat = lat / 10000000.0
                if abs(lng) > 180:
                    lng = lng / 10000000.0

                # יצירת נקודה
                point = {'Lat': lat, 'Lng': lng}

                # הוספה רק אם שונה מהנקודה הקודמת
                if point != previous_point:
                    lat_lng_list.append(point)
                    previous_point = point
                    msg_count += 1

                    # הדפסת התקדמות
                    if msg_count % msg_number_to_show == 0:
                        print(f"Processed {msg_count} points...")

            print(f"Final result: {len(lat_lng_list)} unique points")
            return lat_lng_list

        except Exception as e:
            print(f'error from read_bin_file(): {e}')
            import traceback
            traceback.print_exc()
            return []
#
# class Reader:
#
#     def __init__(self, path):
#         self.path = path
#         try:
#             self.mavlink_connection = mavutil.mavlink_connection(self.path,
#                                                                  robust_parsing=True)
#         except Exception as e:
#             print(f"error connect mavlink: {e}")
#
#     def read_bin_file(self,  msg_number_to_show = 100) -> list:
#         """ get path to .bin file
#         :return list of dictionaries for each flight """
#         try:
#             # create connection of MAVLink
#             lat_lng_list = []
#             run = True
#             previous_point = None
#
#             msg = self.mavlink_connection.recv_match(type= ["GPS"], blocking=False)
#             while True:
#                 if msg is None:
#                     print('msg in none')
#                     run = False
#                     break
#
#                 if msg.get_type() in ["GPS",'GPS_RAW_INT', 'GLOBAL_POSITION_INT']:
#
#                     if hasattr(msg, 'I') == 1 :
#                         lat = hasattr(msg ,"Lat")
#                         lng = hasattr(msg, "Lng")
#
#                         point = {'lat':lat, 'lng':lng}
#
#
#                         if point != previous_point:
#                             lat_lng_list.append(point)
#                             previous_point = point
#
#
#             print("result ",lat_lng_list)
#             return lat_lng_list
#
#         except Exception as e :
#             print(f'error from read_bin_file() : {e}')


if __name__  == "__main__":
    from business_logic.config.config import BIN_FILE_PATH

    r = Reader(BIN_FILE_PATH)
    r.read_bin_file()