import json
import os
from datetime import datetime

import requests
import xlsxwriter


def fetch_gps_positions() -> dict:
    url = "https://ckan2.multimediagdansk.pl/gpsPositions?v=2"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data, status code: ", response.status_code)


def parse_data(data_dir: str, data: dict):
    try:
        data_datetime = datetime.strptime(data["lastUpdate"], "%Y-%m-%dT%H:%M:%SZ")
    except KeyError:
        print("Invalid JSON")
    except ValueError:
        print("Date_string can't be parsed")
    file_name = data_datetime.strftime("%Y-%m-%d") + ".json"
    create_file_if_not_exist(data_dir, file_name)

    file_path = os.path.join(data_dir, file_name)
    with open(file_path, "r+") as f:
        f_data = json.load(f)
        current_time = data_datetime.strftime("%H:%M:%S")
        if current_time in f_data.keys():
            print("This update exist, try again for few seconds.")
        else:
            vehicles = filter_vehicles_data(data, current_time)
            f_data.update({current_time: vehicles})
            f.seek(0)
            json.dump(f_data, f, indent=2)


def filter_vehicles_data(data: dict, current_time) -> dict:
    vehicles = []
    for v in data["vehicles"]:
        if v["tripId"] is None or not v["scheduledTripStartTime"]:
            continue
        scheduledTripStartTime = datetime.strptime(v["scheduledTripStartTime"], "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%H:%M:%S"
        )
        if current_time <= scheduledTripStartTime:
            continue
        vehicles.append(
            {
                "routeShortName": v["routeShortName"],
                "tripId": v["tripId"],
                "headsign": v["headsign"],
                "vehicleId": v["vehicleId"],
                "speed": v["speed"],
                "direction": v["direction"],
                "delay": v["delay"],
                "scheduledTripStartTime": scheduledTripStartTime,
                "lat": v["lat"],
                "lon": v["lon"],
            }
        )
    return vehicles


def create_file_if_not_exist(data_dir: str, file_name: str):
    if not file_name in os.listdir(data_dir):
        with open(os.path.join(data_dir, file_name), "w") as f:
            json.dump({}, f)
            # pass


def create_xlsx(data: dict):
    workbook = xlsxwriter.Workbook("delay.xlsx")
    worksheet = workbook.add_worksheet()
    i = 1
    worksheet.write("A" + str(i), "Delay")
    worksheet.write("B" + str(i), "Count")
    for delay, count in sorted(data.items()):
        i += 1
        worksheet.write("A" + str(i), delay)
        worksheet.write("B" + str(i), count)
    workbook.close()
