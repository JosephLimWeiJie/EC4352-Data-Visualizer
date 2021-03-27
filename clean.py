import gzip
import json
import csv
import re
import sys
from math import cos, asin, sqrt, pi


def loadRawData():
    """
    Returns a list of all resale flats from 2017 to 2021. Note that
    the town name for each flat is abbrievated.
    """
    rawData = []

    with open('./data/resale-flats-2017 to 2021-abbrievated.csv', 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')

        for row in csvReader:
            rawData.append(row)

    return rawData


def loadCurrData():
    """
    Returns a list of resale flat data derived from main.py
    """
    currData = []

    with open('./output/output-uncleaned.csv', 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')

        for row in csvReader:
            currData.append(row)
            
    return currData


def updateEntry(entry, rawData):
    """
    Returns an updated entry where the entry's town name is changed
    to unabbrievated.
    """
    for rawDataEntry in rawData:
        isSame = True
        for i in range(11):
            # index 4 is the abbreviated col
            if (i == 4):
                continue
            else:
                isSame = (entry[i] == rawDataEntry[i])
                if (not isSame):
                    break

        if (isSame):
            entry[4] = rawDataEntry[4]
            return entry


def writeCleanData(headers, rawData, currData):
    """
    Returns a list of resale flats for 2019 with each flat's town name
    being unabbrievated.
    """
    with open('./output/output-cleaned.csv', mode='w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        csvWriter.writerow(headers)
        count = 0

        for entry in currData:
            updatedEntry = updateEntry(entry, rawData)
            csvWriter.writerow(updatedEntry)
            count += 1
        
            print("Process: " + str(count) + "/" + str(len(currData)))
    
    print("Done!")


def main():
    rawData = loadRawData()
    currData = loadCurrData()
    headers = rawData[0]
    writeCleanData(headers, rawData[1:], currData[1:])


if __name__ == "__main__":
    main()