# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:51:15 2020

@author: nilsa
"""

import json
import csv

# this data can be found at https://network.satnogs.org/api/stations/
file = open("logs.json")
raw_data = file.read()
stations_list = json.loads(raw_data)
file.close()

# write the data to a csv file

stations_list.sort(key=lambda stat: stat["id"])

writename = "ground-stations-GPS-extended.csv"
with open(writename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["name", "longitude (deg)", "latitude (deg)", 
                     "altitude (meters)", "minimum horizon (deg)", 
                     "status (1 for Online)", "target utilization", 
                     "UHF frequency [Hz]", "UHF max frequency [Hz]", 
                     "VHF frequency [Hz]", "VHF max frequency [Hz]"])

    ids_written = []
    for station in stations_list:
        if station["id"] in ids_written:
            continue
        else:
            ids_written.append(station["id"])
        row = [station["name"], station["lng"], station["lat"], 
               station["altitude"], station["min_horizon"], 
               int(bool(station["status"] == "Online"))]
        if station["target_utilization"] is not None:
            row.append(station["target_utilization"])
        else:
            row.append(0)

        # add a UHF freq
        for antenna in station["antenna"]:
            if antenna["band"] == "UHF":
                row.append(antenna["frequency"])
                row.append(antenna["frequency_max"])
                break
        if len(row) == 7:
            row.append(0)
            row.append(0)
        # add a VHF freq
        for antenna in station["antenna"]:
            if antenna["band"] == "VHF":
                row.append(antenna["frequency"])
                row.append(antenna["frequency_max"])
                break
        if len(row) == 9:
            row.append(0)
            row.append(0)

        writer.writerow(row)
        
        
        