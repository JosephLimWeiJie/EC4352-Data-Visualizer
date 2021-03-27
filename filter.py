import gzip
import json
import csv
import re
import sys
from math import cos, asin, sqrt, pi


def removeDuplicate(data, listOfPostalCodes):
    """
    Returns a list of unique flat data.
    """
    newData = []

    for d in data:
        # index 11 is the flat's postal code
        if d[11] in listOfPostalCodes:
            continue
        else:
            listOfPostalCodes.append(d[11])
            newData.append(d)
    
    return newData


def loadData():
    data = []
    with open('./output/output-uncleaned.csv', 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if (count == 0):
                count += 1
            else:
                data.append(row)
                count += 1

    return data


def loadDatabase():
    with gzip.open("./data/database.json.gz", "rb") as f:
        database = json.loads(f.read())
        return database


def searchFlatPostalCode(block, townName, altTownName, data):
    for address in data:
        if (block in address['BLK_NO'] and townName in address['ADDRESS']):
            return address['POSTAL']
        elif (block in address['BLK_NO'] and altTownName in address['ADDRESS']):
            return address['POSTAL']


def getFlatData(flatPostalCode, data):
    for d in data:
        if d['POSTAL'] == flatPostalCode:
            return d


def updateData(newData, database):
    """
    Writes a new file containing each flat's latitude and longitude to be used for
    scatter plotting.
    """
    count = 0
    newDataSize = str(len(newData))
    with open('./output/output-for-plot.csv', mode='w') as f:
        writer = csv.writer(f, delimiter=',')
        HEADERS = [
            'month', 'town', 'flat_type', 'block', 'street_name', 'storey_range', 
            'floor_area_sqm', 'flat_model', 'lease_commence_data', 'remaining_lease', 
            'resale_price', 'flat_postal_code', 'min_distance_to_dorm_in_km', 
            'closest_dorm_postal_code', 'distance_to_CBD', 'closest_station_name', 
            'min_distance_to_station_in_km', 'latitude', 'longitude']
        
        writer.writerow(HEADERS)

        for flat in newData:
            # index 3 is flat block number
            # index 4 is flat town name
            flatBlockNum = flat[3]
            flatTownName = flat[1]
            flatAltTownName = flat[4]
            flatPostalCode = searchFlatPostalCode(flatBlockNum, flatTownName, flatAltTownName, database)
            flatData = getFlatData(flatPostalCode, database)

            flat.append(flatData['LATITUDE'])
            flat.append(flatData['LONGITUDE'])
            
            count += 1
            print("Progress: (" + str(count) + "/" + newDataSize + ")")
            writer.writerow(flat)

        print("Done!")


def main():
    listOfPostalCodes = []
    data = loadData()
    database = loadDatabase()
    newData = removeDuplicate(data, listOfPostalCodes)
    updateData(newData, database)   


if __name__ == "__main__":
    main()
