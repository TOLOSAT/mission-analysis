# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 19:34:07 2020

@author: nilsa
"""

import csv

filename = "stations-raw-data.csv"

stations = []

def QTH2GPS(qth_and_alt):
    qth = qth_and_alt.split()[0]
    alt = float(qth_and_alt.split()[1][1:-1])
    
    # field : expect two uppercase letters (see wikipedia article for QTH locator)
    base_lon = -180 + (ord(qth[0])-65)*20
    base_lat = -90 + (ord(qth[1])-65)*10
    # square : expect two digits
    square_lon = base_lon + 2*int(qth[2])
    square_lat = base_lat + 1*int(qth[3])
    # subsquare : expect two lowercase letters
    sub_lon = round(square_lon + (ord(qth[4])-97)*5.0/60 + 2.5/60, 3)
    sub_lat = round(square_lat + (ord(qth[5])-97)*2.5/60 + 1.25/60, 3)

    return sub_lon, sub_lat, alt
    

with open(filename) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    next(spamreader)
    for row in spamreader:
        name = row[1]
        location = row[2]
        lon, lat, alt = QTH2GPS(location)
        station = {"name": name, "longitude (deg)": lon, 
                   "latitude (deg)": lat, "altitude (meters)": alt}
        stations.append(station)

writename = "ground-stations-GPS.csv"
with open(writename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(stations[0].keys())
    for station in stations:
        writer.writerow(station.values())
