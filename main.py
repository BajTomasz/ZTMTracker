import argparse
import json
import os
import sys
import time

import plots as plt
import prepare_data as data

data_dir = "gpsPositionsv2"


def open_data() -> dict:
    vehicles_data = {}
    for file_name in sorted(os.listdir(data_dir)):
        file_path = os.path.join(data_dir, file_name)
        with open(file_path, "r") as f:
            data = json.load(f)
            for time, data in data.items():
                vehicles_data.update({time: data})
    return vehicles_data


def calculate_delay(vehicles_data: dict) -> dict:
    total_delay = 0
    total_vehicle_counter = 0
    delay_data = {}
    ret = {}
    try:
        for date, vehicles in vehicles_data.items():
            sum_delay = 0
            current_vehicle_counter = 0
            for vehicle in vehicles:
                delay = vehicle["delay"]
                current_vehicle_counter += 1
                sum_delay += delay
                if delay not in delay_data:
                    delay_data[delay] = 1
                else:
                    delay_data[delay] += 1                
            current_average_delay = sum_delay / current_vehicle_counter
            total_delay += sum_delay
            total_vehicle_counter += current_vehicle_counter
        average_delay = total_delay / total_vehicle_counter
    except ZeroDivisionError:
        print("Not find vehicles in data")
    else:        
        print("Average delay: %.2f" % average_delay)
        for k, v in sorted(delay_data.items()):
            ret.update({k: v})
    finally:
        return ret



def skip_zero_delay(vehicles_data: dict) -> dict:
    delay_data = {}
    for time, vehicles in vehicles_data.items():
        reducted_vehicles = []
        for vehicle in vehicles:
            if vehicle["delay"] != 0:
                reducted_vehicles.append(vehicle)
        delay_data.update({time, reducted_vehicles})
    return delay_data


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-times", type=int, default=0)
    parser.add_argument("--skip-plot", action="store_true")
    parser.add_argument("--skip-zero-delay", action="store_true")
    args = parser.parse_args()
    fetch_times = args.fetch_times
    skip_plot = args.skip_plot
    skip_zero_delay = args.skip_zero_delay

    for i in range(fetch_times):
        gps_positions_data = data.fetch_gps_positions()
        data.parse_data(data_dir, gps_positions_data)
        time.sleep(10)

    vehicles = open_data()
    if skip_zero_delay:
        vehicles = skip_zero_delay(vehicles)
    delay_data = calculate_delay(vehicles)
    data.create_xlsx(delay_data)
    if not skip_plot and len(delay_data) > 0:
        plt.draw_plot(delay_data)
        plt.draw_quantile_plot(delay_data)


if __name__ == "__main__":
    main(sys.argv[1:])
    # https://ckan.multimediagdansk.pl/dataset/tristar/resource/0683c92f-7241-4698-bbcc-e348ee355076
