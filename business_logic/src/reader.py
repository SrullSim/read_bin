from typing import Any

from pymavlink import mavutil


class Reader:
    """read file in .bin format and extract GPS coordinates"""

    def __init__(self, path):
        self.path = path
        try:
            self.mavlink_connection = mavutil.mavlink_connection(self.path, robust_parsing=True)
        except Exception as e:
            print(f"error connect mavlink: {e}")
            self.mavlink_connection = None

    def read_bin_file(self, msg_number_to_show=2000) -> list[dict[str, Any]]:
        """get path to .bin file
        :return list of dictionaries for each flight"""

        if self.mavlink_connection is None:
            print("No mavlink connection available")
            return []

        try:
            lat_lng_list = []
            previous_point = None
            msg_count = 0

            # loop to read all GPS messages
            while True:
                # reading all GPS messages
                msg = self.mavlink_connection.recv_match(
                    type=["GPS", "GPS_RAW_INT", "GLOBAL_POSITION_INT"], blocking=False
                )

                # if no more messages, exit loop
                if msg is None:
                    print(f"Finished reading. Total points: {len(lat_lng_list)}")
                    break

                # check if message has Lat and Lng attributes
                if not hasattr(msg, "Lat") or not hasattr(msg, "Lng"):
                    continue

                # choose the right GPS source
                if hasattr(msg, "I"):
                    if getattr(msg, "I") != 1:
                        continue

                # get latitude and longitude for each message
                lat = getattr(msg, "Lat")
                lng = getattr(msg, "Lng")

                # check if lat and lng are in degrees or microdegrees
                if abs(lat) > 180:
                    lat = lat / 10000000.0
                if abs(lng) > 180:
                    lng = lng / 10000000.0

                # build point dictionary
                point = {"Lat": lat, "Lng": lng}

                # check for duplicates
                if point != previous_point:
                    lat_lng_list.append(point)
                    previous_point = point
                    msg_count += 1

                    # log progress every msg_number_to_show messages
                    if msg_count % msg_number_to_show == 0:
                        print(f"Processed {msg_count} points")

            print(f"Final result: {len(lat_lng_list)} unique points")
            return lat_lng_list

        except Exception as e:
            print(f"error from read_bin_file(): {e}")
            import traceback

            traceback.print_exc()
            return []


if __name__ == "__main__":
    # for tests
    pass
