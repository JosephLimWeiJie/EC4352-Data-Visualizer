# EC4352 Data Visualizer

This repository contains the program to generate proximity of resales flats (HDB) to the nearest dormitory, CDB district as well as the nearest MRT/LRT stations
in Singapore 2019. The proximity of resales flats to the nearest dormitory is then plotted to derive a heat map for clearer visualization as shown below.

![heatmap](/image/heat-map.png)

## Table of Content
1. Extracting data from relevant data sources
2. Processing data
    - 2.1 Generating proximity data
        - 2.1.1 Proximity of flat to its nearest dormitory
        - 2.1.2 Proximity of flat to the nearest CBD
        - 2.1.3 Proximity of flat to the nearest MRT/LRT stations
        - 2.1.4 Generating an output CSV file
    - 2.2 Cleaning up data
3. Plotting data

## 1. Extracting data from relevant data sources


To calculate the proximity of each flat to its nearest dormitory and the nearest MRT/LRT stations, we have gathered our data from:
- **Singapore Full Postal Code Database**: [OneMap 2020](/data/database.jzon.gz)
- **Resale Flat Data (2019)**: [Resale Flat Prices (Based on Registration Dates), From Jan 2017 onwards](https://data.gov.sg/dataset/resale-flat-prices)
- **List of Dormitories**: [List of Foreign Worker Dormitories](https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/housing/foreign-worker-dormitories#/?page=1&q=)
- **List Of MRT and LRT stations**: Extracted from the Singapore Full Postal Code Database


## 2. Processing Data

### 2.1 Generating proximity data
The main function for processing the data from the relevant data sources is found under `writeResaleFlatDataToCSVFile()`. Before doing so,
we need to convert all the data sources from CSV files to lists in Python so that we can manipulate them. 

```python
with gzip.open("./data/database.json.gz", "rb") as f:
        inputFileName = './data/resale-flats-2019.csv'
        data = json.loads(f.read())
        listOfDormPostalCode = getListOfDormPostalCode()
        listOfResaleFlat = getListOfResaleFlat(inputFileName)
        listOfDorm = getListOfDorm()
        listOfStations = getListOfStations()
 ```
Each method and its description are documented in `main.py`.

#### 2.1.1 Proximity of flat to its nearest dormitory
To calculate the proxmity, we have used the [Haversine Formula.](https://www.movable-type.co.uk/scripts/latlong.html) For simplicity, the formula takes in the latitude
and longitude of 2 points and returns the distance between 2 points in kilometres as show in `calculateDistance()`.

```python
def calculateDistance(lat1, lon1, lat2, lon2):
    """
    Returns the distance between 2 points using the haversine formula that
    takes in the latitude and longitudes of the 2 points.
    """
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 12742 * asin(sqrt(a))
```


#### 2.1.2 Proximity of flat to the nearest CBD
For this, we use the same `calculateDistance()` to find the distance between a flat to the CDB. In our case, we have assumed that the CDB has the following latitude and
longitude.

```python
CBD_LATITUDE = 1.284297 
CBD_LONGITUDE = 103.851053
```

#### 2.1.3 Proximity of flat to the nearest MRT/LRT stations
Similarly, `calculateDistance()` is used.

#### 2.1.4 Generating an output CSV file 
Due to the different format of each csv file used from the relevant data sources, some files did not come with the necessary data to compute the proximity. 

**Problems**:
1. The dormitories data extracted comes with their respective postal codes, but without latitude and longitude. 
2. The list of resale flat data did not come with their postal codes, latitude and longitude.

To resolve this, there is a need to consistently query the database. In this case, we will query against the same database, found in `data/database.json.gz` 
that contains all Singapore Postal Codes.

**Solutions**:
1. To get the latitude and longitude of each dormitories, we query against the database by supplying the dormitory's postal code to see if there is a match using 
`getDormData()`.

```python
def getDormData(dormPostalCode, data):
    """
    Returns a dorm's data by querying the database against the dorm's postal code.
    """
    for d in data:
        if d['POSTAL'] == dormPostalCode:
            return d
```

2. Getting the latitude and longitude for each resale flat data is problematic as the data source did not come with postal codes. As such, we have to break this
down into 2 steps.

First, we query the database by using `searchFlatPostalCode()` to get the postal code for each flat.

```python
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
```
Next, once we have the flat's postal code, we can extract the full flat data using `getFlatData()`.

```python
def getFlatData(flatPostalCode, data):
    """
    Returns a flat's data by querying the database against the flat's postal code.
    """
    for d in data:
        if d['POSTAL'] == flatPostalCode:
            return d
```

With these, we can calculate the proximity of each flat to the closest dormitory. We do this by simply calculating the distance of a flat to all other dormitories
and then use a `min()` function to find the minimum distance. The relevant code logic is:

```python
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
```

We also do the same to get the flat's distance to the CBD using:

```python
distanceFromCBD = calculateDistance(CBD_LATITUDE, CBD_LONGITUDE, float(flatLatitude), float(flatLongitude))
flat.append(distanceFromCBD)
```

Finally, we apply the same logic above to compute the proximity of each flat to the nearest MRT/LRT stations. The relevant code logic is:

```python
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
```

With all the relevant proximity of the flat to the nearest dormitory, CBD and MRT/LRT stations, we write them into a new file named`output-uncleaned.csv` which can
be found under `output/output-uncleaned.csv`, ready to be cleaned in the next step.

### 2.2 Cleaning data
As the `output-uncleaned.csv` comes with unabbrievated town name for each flat entry, this is not consistent with the format that we will be using for regression 
analysis. We then clean this data by running `clean.py` file.

Basically, the main logic of the cleaning is found under `updateEntry()` function. What this does is that we compare each flat data in `output-uncleaned.csv` 
against the `resale-flats-2017 to 2021-abbrievated.csv` and update accordingly. The logic is:

```python
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
```

## 3. Plotting data
To visualise each flat's proximity to their nearest dormitories, we need to further filter down our current flat data in `output-uncleaned.csv` file by running 
`filter.py`. The reason for doing this is that we have about 22,000 entries in the output file, of which many of these are considered duplicates as they have
the same postal codes. 

To remove duplicates, we supply data from `output-uncleaned.csv` and store it in a list structure under `listOfPostalCodes`. We then skip entries whose postal codes are already present in the `listOfPostalCodes`. The main logic is as follows:

```python
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
```

Then, with the list of unique postal codes, we generate a list of unique resale flats data, along with their longitudes and latitudes using `updateData()` method
and output them onto `output-for-plot.csv` file to be used for plotting.

The process is very similar to the previous section, except that we are appending latitude and longitude to each flat data. The logic is:

```python
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
```

Now that we have the relevant filtered data in `output-for-plot.csv`, we are now ready to visualize these data points onto a heat map. We do this by running `plot.py`.

The main logic for generating the heat map is using `plotData()`, which has the logic of:

```python
def plotData(flatData):
    """
    Plots a scatter plot with a heatmap from the list of resale flat data.
    """
    singapore_img = mpimg.imread('./image/singapore.png')

    ax = flatData.plot(kind="scatter", x="longitude", y="latitude", figsize=(10,7),
                        label="Resale Flats", c="min_distance_to_dorm_in_km", cmap=plt.get_cmap("jet"),
                        colorbar=True, alpha=0.4)

    # extent = [left, right, down, up]
    # original extent = [103.67, 104.00, 1.26, 1.47]
    # 103.64, 104.02, 1.22, 1.49
    plt.imshow(singapore_img, extent=[103.64, 104.02, 1.22, 1.49], alpha=0.5)
    plt.ylabel("Latitude", fontsize=14)
    plt.xlabel("Longitude", fontsize=14)
    plt.legend(fontsize=16)
    plt.show()
```

You can also find the heat map image in `image/heat-map.png`.

