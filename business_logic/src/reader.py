import csv
from typing import Any
from pymavlink import mavutil



class Reader:

    def __init__(self, path):
        self.path = path
        try:
            self.mavlink_connection = mavutil.mavlink_connection(self.path,
                                                                 robust_parsing=True)
        except Exception as e:
            print(f"error connect mavlink: {e}")

    def read_bin_file(self,  msg_number_to_show = 100) -> list | None:
        """ get path to .bin file
        :return list of dictionaries for each flight """
        try:
            # create connection of MAVLink
            lat_lng_list = []
            run = True
            previous_point = None

            msg = self.mavlink_connection.recv_match(type= ["GPS"], blocking=False)
            while run:
                if msg is None:
                    print('msg in none')
                    run = False
                    break

                if msg.get_type() in ["GPS",'GPS_RAW_INT', 'GLOBAL_POSITION_INT']:

                    if hasattr(msg, 'I') == 1 :
                        lat = hasattr(msg ,"Lat")
                        lng = hasattr(msg, "Lng")

                        point = {'lat':lat, 'lng':lng}


                        if point != previous_point:
                            lat_lng_list.append(point)
                            previous_point = point


            print("result ",lat_lng_list)



        except Exception as e :
            print(f'error from read_bin_file() : {e}')


if __name__  == "__main__":
    from business_logic.config.config import BIN_FILE_PATH

    r = Reader(BIN_FILE_PATH)
    r.read_bin_file()