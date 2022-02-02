from HelperMethods import readDataForList, getCaseType
from locationiq.geocoder import LocationIQ
import pandas as pd 
import time
from datetime import datetime, timedelta
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import CRS, Proj, transform
import numpy as np
import os

# Script:   DashboardMapGenerator.py
# Purpose:  This script handles the map portion of the dashboard. It looks for cases that aren't geocoded, assigned as latitute/longitude coordinates, then caches the results.
#			Next, it uses uniform hexes in Jackson County, and counts points by uniform hex. It does this by case categories
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, GeoPandas, LocationIQ, datetime, shapley, pyproj, numpy, os
#	 Functions: readDataForList, getCaseType


# Function:  findNonGeocodedCases
# Purpose:   This function finds the addresses that haven't been geocoded yet
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: addressDictionary (dataFrame of addresses associated with file numbers), xls (list of dataframes of caseTypes - received, filed, disposed, not-filed)
# Return:    Returns a dataframe of cases with no geocoding
def findNonGeocodedCases(addressDictionary, xls):
	
	#Gets a list of all the file numbers that have been geocoded
	geocodedAddressList = addressDictionary['File #'].tolist()

	#Initialize lists and blank dataframe
	nonGeocodedAddressFileNumbers = []
	nonGeocodedAddresses = []
	nonGeocodedAddressDataFrame = pd.DataFrame()

	#Loop Through Each CaseType
	for caseType in xls:
		#Drop Duplicate File Numbers
		caseType = caseType.drop_duplicates(subset=['File #'])
		
		#Filter Out the dataframes that have already been geocoded
		caseType = caseType[~caseType['File #'].isin(geocodedAddressList)]

		#Add the addresses and file numbers to our non-geocoded addresses
		nonGeocodedAddressFileNumbers.extend(caseType['File #'].tolist())
		nonGeocodedAddresses.extend(caseType['Offense Street Address'].tolist())

	#If there aren't any, return the empty dataframe
	if len(nonGeocodedAddresses)==0:
		return nonGeocodedAddressDataFrame

	#Add the addresses and file numbers the non-Geocoded dataframe
	nonGeocodedAddressDataFrame['File #'] = nonGeocodedAddressFileNumbers
	nonGeocodedAddressDataFrame['Street Address'] = nonGeocodedAddresses

	#Cleaning Up Addresses - Replacing Blank Addresses
	nonGeocodedAddressDataFrame['Street Address'] = nonGeocodedAddressDataFrame['Street Address'].astype(str).str.replace(', , , , ', ',')
	nonGeocodedAddressDataFrame['Street Address'] = nonGeocodedAddressDataFrame['Street Address'].str.replace(', , , ', ',')
	nonGeocodedAddressDataFrame['Street Address'] = nonGeocodedAddressDataFrame['Street Address'].str.replace(', , ', ',')
	nonGeocodedAddressDataFrame['Street Address'] = nonGeocodedAddressDataFrame['Street Address'].str.replace('.0', '')
	
	#Dropping NA/Duplicate Addresses and resetting index
	nonGeocodedAddressDataFrame = nonGeocodedAddressDataFrame.drop_duplicates(subset=['File #'])
	nonGeocodedAddressDataFrame = nonGeocodedAddressDataFrame.dropna(subset=['Street Address'])
	nonGeocodedAddressDataFrame = nonGeocodedAddressDataFrame.reset_index()

	return nonGeocodedAddressDataFrame

# Function:  geocodeCases
# Purpose:   This function geocodes the addresses that have been identified as "non-geocoded"
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: addressDictionary (dataFrame of addresses associated with file numbers), nonGeocodedAddressDataFrame (dataframe of addresses that haven't been geocoded yet)
# Return:    Returns a dataframe of cases with no geocoding

def geocodeCases(addressDictionary, nonGeocodedAddressDataFrame):

	#If there aren't any addresses to geocode, return false
	if len(nonGeocodedAddressDataFrame.index)==0:
		return False

	#Initialize Lists
	allLatitude = []
	allLongitude = []
	allFileNumbers = []
	allStreetAddresses = []

	text_file = open("key.txt", "r")
	key = text_file.read()
	
	#Loop Through Each non-geocoded address
	for i, row in nonGeocodedAddressDataFrame.iterrows():
		
		#Initialize Coordinates and completed geocoding dataframe
		completedGeocoding = pd.DataFrame()
		tempCoordinates = []
		#Load geocoder with API Key
		geocoder = LocationIQ(key)

		#Try This - if errors, put the point at null island
		try:
			h = geocoder.geocode(row["Street Address"])
			latitude = [h[0]['lat']]
			longitude = [h[0]['lon']]

		except:
			latitude = [0]
			longitude = [0]

		#Extend the Completed Lists
		allFileNumbers.extend([row['File #']])
		allStreetAddresses.extend([row["Street Address"]])
		allLatitude.extend(latitude)
		allLongitude.extend(longitude)

		#Sleep to give the geocoder a break
		time.sleep(1)

		#Update the geocoding dataframe
		completedGeocoding['File #'] = allFileNumbers
		completedGeocoding['Street Address'] = allStreetAddresses
		completedGeocoding['Latitude'] = allLatitude
		completedGeocoding['Longitude'] = allLongitude

		#Print out the update
		print(str(i+1) + " out of " + str(len(nonGeocodedAddressDataFrame.index) + 1) + " " + str(row['File #']) + " " + row['Street Address'] + " " + str(longitude) +" " +str(latitude))

	#Sets the coordinates as floats
	completedGeocoding['Latitude'] = completedGeocoding['Latitude'].astype(float)
	completedGeocoding['Longitude'] = completedGeocoding['Longitude'].astype(float)

	#Appends to the updated address dictionary, and resets the index
	addressDictionary = addressDictionary.append(completedGeocoding)
	addressDictionary.reset_index()

	#Exports it as a CSV when it's finisehd
	addressDictionary.to_csv("HelperDatasets\\AddressDictionary.csv", index = False, encoding = 'utf-8')

# Function:  pointsInPolygons
# Purpose:   This function takes a dataframe of charged cases, then counts the number of points per hex
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: year (integer of year), tempCaseCategory (string of case category), tempCaseStage (string of case stage), tempCaseCategoryDataFrame (filtered dataframe of case categories)
# Return:    Returns a dataframe of cases with no geocoding
def pointsInPolygons(year, tempCaseCategory, tempCaseStage, tempCaseCategoryDataFrame):

	#Set CRS
	crs = 'epsg:4326'

	#Load Jackson County Hexes (Pre-Determined)
	JacksonCountyHexes = gpd.GeoDataFrame.from_file("Maps\\JacksonCountyHexes.geojson").to_crs(crs)
	
	#Drops Duplicates to Get Individual Cases
	tempCaseCategoryDataFrame = tempCaseCategoryDataFrame.drop_duplicates(subset=['File #'])
	
	#Set Index as ObjectID
	JacksonCountyHexes['objectid'] = JacksonCountyHexes.index
	
	#Set Geometry as latitutde and longitude points
	geometry = [Point(xy) for xy in zip(tempCaseCategoryDataFrame['Longitude'], tempCaseCategoryDataFrame['Latitude'])]
	
	#Create a DataFrame with those geocoded points
	points = gpd.GeoDataFrame(tempCaseCategoryDataFrame, crs=crs, geometry=geometry)

	#Creates a border, then filters the points within Jackson County's Border
	JacksonCountyBorder = JacksonCountyHexes.geometry.unary_union
	points = points[points.geometry.within(JacksonCountyBorder)]

	#If the points dataframe is empty, return false
	if len(points.index)==0:
		return False

	#Creates a New Column with C
	points['Case'] = "Cases"

	#Does a spatial join to join Points with Polygons
	dfsjoin = gpd.sjoin(JacksonCountyHexes, points) #Spatial join Points to polygons
	
	#Makes a pivot table 
	dfpivot = pd.pivot_table(dfsjoin,index='objectid', columns='Case',aggfunc={'Case':len})
	
	#Drops Level on those columns
	dfpivot.columns = dfpivot.columns.droplevel()
	
	#Merges those into a new dataframe
	dfpolynew = JacksonCountyHexes.merge(dfpivot, how='left',on='objectid')

	
	#Drop the Hexes that don't have any points
	dfpolynew = dfpolynew[dfpolynew['Cases']>0]

	#Adding Columns for Later Concatenation
	dfpolynew['Year'] = str(year)
	dfpolynew['Cases'] = dfpolynew['Cases'].astype(str)

	if tempCaseCategory == "All":
		dfpolynew['Case Category'] = "*All"
	else:
		dfpolynew['Case Category'] = tempCaseCategory
	
	dfpolynew['Case Stage'] = tempCaseStage

	#Export json based on year and case stage
	dfpolynew.to_file("Maps\\TempDataForMap\\"+tempCaseStage+"-"+str(year) + "-" + tempCaseCategory+".json", driver = "GeoJSON")

# Function:  countPointsinHexes
# Purpose:   This function loops through each case category, and generates cases per hex
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: addressDictionary, chargesDictionary, xls, year
# Return:    None
def countPointsinHexes(addressDictionary, chargesDictionary, xls, year):
	#Get a list of charge code categories
	listOfChargeCategories = list(set(chargesDictionary['Category'].tolist()))

	#Initialize Case Label
	caseLabel = 0

	#For Each case Type
	for caseType in xls:

		#Merge in Charges Dictionary and Addresses for Points
		caseType = pd.merge(caseType, chargesDictionary, on ='Ref. Charge Code', how ='left')
		caseType = pd.merge(caseType, addressDictionary, on ='File #', how ='left')

		#Get the label for the temp case Stage
		tempCaseStage = getCaseType(caseLabel)

		#Loop Through Each List of Charge Code Categories
		for tempCaseCategory in listOfChargeCategories:

			#Filter Down by that category
			tempCaseCategoryDataFrame = caseType[caseType['Category']==tempCaseCategory]
			
			#If the dataframe isn't empty, call points in polygons to count up the points per hexes
			if len(tempCaseCategoryDataFrame.index)!=0:
				pointsInPolygons(year, tempCaseCategory, tempCaseStage, tempCaseCategoryDataFrame)

		#Run Points in polygons for a non-filtered dataframe to get a broader picture
		pointsInPolygons(year, "All", tempCaseStage, caseType)

		#Increment Case Label By 1
		caseLabel = caseLabel + 1


# Function:  concatenateGeoDataFrame
# Purpose:   This Function Concatenates the Gigantic DataFrame of all the various points
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: 
# Return:    
def concatenateGeoDataFrame():
	#Initialize It
	hugeDataFrame = gpd.GeoDataFrame()

	#Get The Base Directory for All The Data
	baseDirectory = "Maps\\TempDataForMap\\"

	#Get a a list of all the items in the base directory
	file = os.listdir(baseDirectory)
	#Get A List to Generate Paths
	path = [os.path.join(baseDirectory, i) for i in file if ".json" in i]

	#Concatenate the GeoDataFrame
	hugeDataFrame = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in path], ignore_index=True), crs=gpd.read_file(path[0]).crs)

	#Drop The Columns that we don't need
	hugeDataFrame = hugeDataFrame.drop(columns=['objectid', 'left', 'bottom', 'right', 'top'])

	#Convert the dataframe to the correct CRS
	hugeDataFrame = hugeDataFrame.to_crs(gpd.read_file(path[0]).crs)

	#Export, import, export to make sure all the file headers are correct
	hugeDataFrame.to_file("Maps\\MasterSpatialDataV2.GeoJSON", driver= "GeoJSON", index = False)
	hugeDataFrame = gpd.GeoDataFrame.from_file("Maps\\MasterSpatialDataV2.geojson").to_crs(gpd.read_file(path[0]).crs)
	hugeDataFrame.to_file("Maps\\MasterSpatialDataFixedV2.geojson", driver= "GeoJSON", index=False)


# Function:  geocoderRunner
# Purpose:   This handles all the geocoding for the Karpel Dashboard
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of dataframes of various case types), year (int of year)
# Return:    
def geocoderRunner(xls, year):

	#Load Charges and Address Dictionary
	chargesDictionary = pd.read_csv("HelperDatasets\\ChargeCodeCategories.csv", encoding = 'utf-8')
	addressDictionary = pd.read_csv("HelperDatasets\\AddressDictionary.csv", encoding = 'utf-8')

	#Get Non-Geocoded Addresses
	nonGeocodedAddressDataFrame = findNonGeocodedCases(addressDictionary, xls)

	#Geocode Non-Geocoded Cases
	geocodeCases(addressDictionary,nonGeocodedAddressDataFrame)

	#Count Up the Points in Each Hex
	countPointsinHexes(addressDictionary, chargesDictionary, xls, year)

	#Concatenate All The Various DataFrames, then Export it
	concatenateGeoDataFrame()