import gzip
import json
import csv
import re
import sys
from math import cos, asin, sqrt, pi


CBD_LATITUDE = 1.284297 
CBD_LONGITUDE = 103.851053


def calculateDistance(lat1, lon1, lat2, lon2):
    """
    Returns the distance between 2 points using the haversine formula that
    takes in the latitude and longitudes of the 2 points.
    """
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 12742 * asin(sqrt(a))


def getNearbyBuildingsFromDorm(dormData, data, proximity):
    """
    Returns a list of buildings that are within a certain proximity to a dorm.
    """
    dormLatitude = dormData['LATITUDE']
    dormLongitude = dormData['LONGITUDE']

    buildingsNearDorm = []

    for d in data:
        dLatitude = d['LATITUDE']
        dLongitude = d['LONGITUDE']
        distance_apart = calculateDistance(float(dormLatitude), float(dormLongitude), float(dLatitude), float(dLongitude))
        if (distance_apart <= proximity):
            buildingsNearDorm.append(d)

    return buildingsNearDorm


def getListOfDormPostalCode():
    """
    Returns a list of all dorms' postal codes.
    """
    dormPostalCodes = []
    with open('./data/dorm-postal-codes.csv', 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if (count == 0):
                count += 1
            else:
                # index for postal code is 3
                rawPostalCode = row[3]
                cleanPostalCode = rawPostalCode[1:]
                dormPostalCodes.append(cleanPostalCode)
                count += 1

    return dormPostalCodes


def getListOfResaleFlat(inputFileName):
    """
    Returns a list of all resale flats.
    """
    resaleFlats = []
    with open(inputFileName, 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if (count == 0):
                count += 1
            else:
                # index for postal code is 2
                resaleFlats.append(row)
                count += 1

    return resaleFlats


def getListOfDorm():
    """
    Returns a list of dorm that includes each dorm's data.
    """
    dorms = []
    with open('./data/dorm-postal-codes.csv', 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if (count == 0):
                count += 1
            else:
                # index for postal code is 4
                rawPostalCode = row[4]
                cleanPostalCode = rawPostalCode[1:]
                row[4] = cleanPostalCode
                dorms.append(row)
                count += 1

    return dorms


def getListOfStations():
    """
    Returns a list of stations (inclusive of MRT and LRT stations).
    """
    stations = []
    with open('./data/mrt_lrt_data.csv', 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if (count == 0):
                count += 1
            else:
                # index for postal code is 4
                stationName = row[0]
                latitude = row[5]
                longitude = row[6]
                stations.append([stationName, latitude, longitude])
                count += 1

    return stations


def getFlatData(flatPostalCode, data):
    """
    Returns a flat's data by querying the database against the flat's postal code.
    """
    for d in data:
        if d['POSTAL'] == flatPostalCode:
            return d


def getDormData(dormPostalCode, data):
    """
    Returns a dorm's data by querying the database against the dorm's postal code.
    """
    for d in data:
        if d['POSTAL'] == dormPostalCode:
            return d


def searchFlatPostalCode(block, townName, altTownName, data):
    """
    Searches the database and returns the flat postal code if found.
    The search is done by querying the database for the BLK_NO and ADDRESS
    and then BLK_NO and POSTAL if the former fails.
    """
    for address in data:
        if (block in address['BLK_NO'] and townName in address['ADDRESS']):
            return address['POSTAL']
        elif (block in address['BLK_NO'] and altTownName in address['ADDRESS']):
            return address['POSTAL']


def getDormDataFromDatabase(simplifiedTownName, postalCode, data):
    """
    Returns a list of dorms that matches a given town name and postal code
    when querying against the database.
    """
    dormData = []

    for d in data:
        if (simplifiedTownName in d['ADDRESS'] and postalCode in d['POSTAL']):
            dormData.append(d)

    return dormData


def writeHeader():
    """
    Writes the header for the output file.
    """
    with open('./output/output-uncleaned.csv', mode='w') as resaleDataFile:
        resaleDataWriter = csv.writer(resaleDataFile, delimiter=',')
        HEADERS = [
            'month', 'town', 'flat_type', 'block', 'street_name', 'storey_range', 
            'floor_area_sqm', 'flat_model', 'lease_commence_data', 'remaining_lease', 
            'resale_price', 'flat_postal_code', 'min_distance_to_dorm_in_km', 
            'closest_dorm_postal_code', 'distance_to_CBD', 'closest_station_name', 'min_distance_to_station_in_km']

        resaleDataWriter.writerow(HEADERS)


def writeResaleFlatDataToCSVFile(listOfResaleFlat, listOfDorm, listOfStations, data, numOfTotalData):
    """
    Writes the output file. The output file will contain each flat's mininum distance to 
    the nearest dorm, distance to CBD, and the minimum distance to the nearest MRT/LRT 
    station.
    """
    with open('./output/output-uncleaned.csv', mode='a', newline='') as resaleDataFile:
        writeHeader()

        resaleDataWriter = csv.writer(resaleDataFile, delimiter=',')
        count = 0
        success = 0
        fail = 0
    
        for flat in listOfResaleFlat:
            # index 3 is flat block number
            # index 4 is flat town name
            flatBlockNum = flat[3]
            flatTownName = flat[1]
            flatAltTownName = flat[4]
            flatPostalCode = searchFlatPostalCode(flatBlockNum, flatTownName, flatAltTownName, data)
            if (flatPostalCode is None):
                count += 1
                fail += 1
                continue
            else:
                flat.append(flatPostalCode)
                # find flat in data
                flatData = getFlatData(flatPostalCode, data)
                
                # get min distance from block to dorm
                MIN_DIST = sys.maxsize
                dorm_postal = ""
                flat.append(MIN_DIST)
                flat.append(dorm_postal)
                for dorm in listOfDorm:
                    # index 1 is simplified town name
                    # index 4 is dorm postal code
                    dormTownName = dorm[1]
                    dormPostalCode = dorm[4]
                    if dormTownName == "NULL":
                        continue
                    else:
                        dormData = getDormDataFromDatabase(dormTownName, dormPostalCode, data)
                        #print(dormData)
                        for d in dormData:
                            dormLatitude = d['LATITUDE']
                            dormLongitude = d['LONGITUDE']
                            flatLatitude = flatData['LATITUDE']
                            flatLongitude = flatData['LONGITUDE']
                            distanceApart = calculateDistance(float(dormLatitude), float(dormLongitude), float(flatLatitude), float(flatLongitude))

                            if distanceApart < MIN_DIST:
                                MIN_DIST = distanceApart
                                dorm_postal = d['POSTAL']
                
                                flat[len(flat) - 2] = distanceApart
                                flat[len(flat) - 1] = dorm_postal
                
                # get distance to CBD
                distanceFromCBD = calculateDistance(CBD_LATITUDE, CBD_LONGITUDE, float(flatLatitude), float(flatLongitude))
                flat.append(distanceFromCBD)
                
                # get distance to nearest mrt/lrt
                closestStation = listOfStations[0]
                minDistanceToStation = sys.maxsize
                closestStationName = ""
                for station in listOfStations:
                    # index 0 -> stationName
                    # index 1 -> latitude
                    # index 2 -> longitude
                    calDistance = calculateDistance(float(station[1]), float(station[2]), float(flatData['LATITUDE']), float(flatData['LONGITUDE']))
                    if (calDistance < minDistanceToStation):
                        minDistanceToStation = calDistance
                        closestStationName = station[0]
                
                flat.append(closestStationName)
                flat.append(minDistanceToStation)
                
                count += 1
                success += 1
                print("Updating file ... (" + str(count) + "/" + str(numOfTotalData) + ")   Left: (" + str(numOfTotalData - count) + ")   Success: " + str(success) + " Fail: " + str(fail))
        
            resaleDataWriter.writerow(flat)


def getLenOfOutputFile():
    """
    Returns the number of entries in the output file.
    """
    count = 0
    with open('./output/output-uncleaned.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            count += 1

    return count


def getListOfMrtStations():
    """
    Returns a list of MRT/LRT stations.
    """
    count = 0
    with open('./data/mrt_lrt_data.csv', "r") as file:
        reader = csv.reader(file)
        for row in reader:
            count += 1
    return count


def main():
    """
    Loads all relevant data and write to a new output file.
    """
    with gzip.open("./data/database.json.gz", "rb") as f:
        inputFileName = './data/resale-flats-2019.csv'
        data = json.loads(f.read())
        listOfDormPostalCode = getListOfDormPostalCode()
        listOfResaleFlat = getListOfResaleFlat(inputFileName)
        listOfDorm = getListOfDorm()
        listOfStations = getListOfStations()
    
        numOfTotalData = len(listOfResaleFlat)
        
        writeResaleFlatDataToCSVFile(listOfResaleFlat, listOfDorm, listOfStations, data, numOfTotalData)


if __name__ == "__main__":
    main()
