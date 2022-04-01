import pandas as pd 
import os
import datetime
from datetime import datetime, timedelta, date
import shutil

# Script:   HelperMethods.py
# Purpose:  This script provides helper methods for the karpelDashboard
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, os, shutil, datetime
#	 Functions: KarpelStarter, DefendantDemographics, Case Details, HelperMethods, DashboardMapGenerator, DataUploaderRunner

# Function:  getNewestFile
# Purpose:   This function gets the latest date (or most recent file) from the Karpel Weekly Data Drop
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: weeklyUpload (FilePath Location of Karpel Data Drop)
# Return:    Returns a string of the most recent value (20210323)
def getNewestFile(weeklyUpload):

	#Initializes Blank List 
	allDates = []

	#Loops through the Weekly Data Drop Folder
	for item in os.listdir(weeklyUpload):

		#Pulls the Date from Each File in the Folder
		date = int(item.split("_")[1])

		#Appends it to a list
		allDates.append(date)

	#Removes all the duplicates
	allDates = list(set(allDates))

	#Sorts the List without Duplicates
	allDates.sort()

	#Grabs the most recent file
	mostRecent = str(allDates[-1])

	#Returns that most recent file. 
	return mostRecent

# Function:  getUniqueListOfFiledCases
# Purpose:   This function gets a list of all the filed file numbers over the last 5 years. If a case has ever been filed, it's in this list.
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: weeklyUpload (FilePath Location of Karpel Data Drop)
# Return:    Returns a list of unique filed cases
def getUniqueListOfFiledCases(weeklyUpload):
	#Get Old List of Filed Cases Numbers (Pre-Current Year)
	filedCases = pd.read_csv("HelperDatasets\\FiledFileNumbers.csv", encoding = 'utf-8')

	#Get Newest Filed Cases
	directoryList = os.listdir(weeklyUpload)
	
	#Get newest filed cases
	newestFile = getNewestFile(weeklyUpload)
	newestFiledCases = pd.read_csv(weeklyUpload + "Fld_" + str(newestFile) + "_1800.CSV", encoding = 'utf-8')
	
	#Filter the dataset down to just file numbers
	newestFiledCases = newestFiledCases[['File #']]

	#Append the new filed cases to the list of older filed cases

	frames = []
	frames.append(filedCases)
	frames.append(newestFiledCases)

	filedCases = pd.concat(frames)
	#filedCases = filedCases.append(newestFiledCases)

	#Drop duplicates to get unique ones
	filedCases = filedCases.drop_duplicates(subset='File #')

	#export it as a list
	filedFileNumbers = filedCases['File #'].tolist()

	return filedFileNumbers

# Function:  getCaseYear
# Purpose:   This function returns the case year from a list of cases
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed dataframes)
# Return:    Returns an integer as year
def getCaseYear(xls):

	#initialize set
	yearList = set()

	#loop through case types
	for caseType in xls:

		#If casetype is empty, skip it
		#if caseType.empty:
		#	race[caseLabel] = 0
		#	caseInput = caseInput + 1
		#	continue

		#Export a set of years
		tempYear = list(set(caseType['Year'].tolist()))[0]
		
		#Append to a list (it'll always be 1 element long)
		yearList.add(tempYear)

	#Get just the year as an int
	year = list(yearList)[0]

	#Return the year int
	return year

# Function:  getCaseType
# Purpose:   Helper Method to return the type of case based on an input
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: caseInput (int)
# Return:    Returns a String of the cas type label
def getCaseType(caseInput):
	if caseInput == 0:
		return "Received"

	if caseInput == 1:
		return "Not-Filed"

	if caseInput == 2:
		return "Filed"

	if caseInput == 3:
		return "Disposed"


# Function:  getListOfCrimeCategories
# Purpose:   Method to load the list of charge code categories
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: 
# Return:    Returns a list of charge code categories
def getListOfCrimeCategories():
	crimeCategoryList = []

	chargesDictionary = pd.read_csv("HelperDatasets\\ChargeCodeCategories.csv", encoding = 'utf-8')
	crimeCategoryList = list(set(chargesDictionary["Category"].tolist()))

	return crimeCategoryList

# Function:  dropCurrentCases
# Purpose:   Method to drop all current cases from CombinedData.CSV
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: Year (int)
# Return:    noCurrentCasesCombinedDataFrame (Dataframe without that year)
def dropCurrentCases(year):

	#Read Combined Data
	combinedDataDF = pd.read_csv("CombinedDataV2.csv", encoding = 'utf-8')
	
	#Filter out year
	noCurrentCasesCombinedDataFrame = combinedDataDF[combinedDataDF['Year']!=year]

	#Return it
	return noCurrentCasesCombinedDataFrame

# Function:  combineAllCSVs
# Purpose:   Method to Combine all the CSVs from DataForDashboard into One For Upload
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: Year (int)
# Return:    None
def combineAllCSVs(year):
	#load combined data, dropping the current year
	combinedData = dropCurrentCases(year)

	#Getting Directory Where all the data analysis is
	Directory = "DataForDashboard\\"

	#Initializing getListOfCrimeCategories
	dataSource = []
	itemName = []
	year = []
	received = []
	notFiled = []
	filed = []
	disposed = []
	caseCategory = []

	#Loop Through Each Element in DataForDashboard
	for item in os.listdir(Directory):

		#Load the CSV
		spreadsheet = pd.read_csv(Directory+item)
		
		#Get A List of the columns
		columns = spreadsheet.columns.tolist()

		#For Each Row, Append it to the list
		for i, row in spreadsheet.iterrows():
			tempDataSource = item.split(".")[0]
			tempDataSource = item.split(" - ")[1]
			dataSource.append(tempDataSource)
			itemName.append(row['Item'])
			year.append(row["Year"])
			received.append(row['Received'])
			notFiled.append(row['Not-Filed'])
			filed.append(row["Filed"])
			disposed.append(row['Disposed'])
			caseCategory.append(row['caseCategory'])

	#Initialize Current Year DataFrame, then append all those lists
	currentYear = pd.DataFrame()
	currentYear['dataSource'] = dataSource
	currentYear['Item'] = itemName
	currentYear['Year'] = year
	currentYear['Received'] = received
	currentYear['Not-Filed'] = notFiled
	currentYear['Filed'] = filed
	currentYear['Disposed'] = disposed
	currentYear['caseCategory'] = caseCategory
	
	#Appending The DataFrame to Combined Data

	frames = []
	frames.append(currentYear)
	frames.append(combinedData)

	currentYear = pd.concat(frames)

	#currentYear = currentYear.append(combinedData)

	#Replacing All with *All
	currentYear.loc[(currentYear.caseCategory == 'All'),'caseCategory']='*All'

	#Exporting DataFrame to CSV
	currentYear.to_csv("CombinedDataV2.csv", encoding='utf-8', index = False)

# Function:  readDataForList
# Purpose:   Method to Read All Data into one list of dataframes
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: None
# Return:    xls (list of received, not-filed, filed, and disposed dataframes)
def readDataForList():

	#initialize list
	xls = []

	#Get Directory of Karpel Data Drop
	weeklyUpload = "H:\\Units Attorneys and Staff\\01 - Units\\DT Crime Strategies Unit\\Weekly Update\\"

	#For Each Item in the data folder
	for item in os.listdir("RawData"):

		#Load the csv file
		xl = pd.read_csv('RawData\\'+item)
		
		#If it's a not-filed case, drop out the file numbers that have been filed
		if "Not Filed" in item:
			uniqueFiledCRNs = getUniqueListOfFiledCases(weeklyUpload)
			xl = xl[~xl['File #'].isin(uniqueFiledCRNs)]

			#Reset the index
			xl = xl.reset_index()
		#Append the caseType to the master list, then return it
		xls.append(xl)
	return xls

# Function:  filterLargerDataFrame
# Purpose:   Method to Filter DataFrame based on charge code category
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of case types - received, filed, not-filed, disposed), caseCategory (string of case category)
# Return:    filtered dataframe
def filterLargerDataFrame(xls, caseCategory):
	#Initialize List
	filteredXLS = []

	#Load Charge Code Categories
	chargesDictionary = pd.read_csv("HelperDatasets\\ChargeCodeCategories.csv", encoding = 'utf-8')

	#Initialize blank counts
	blankCount = 0 
	for caseType in xls:

		#Merge In Case Charges
		caseType = caseType.merge(chargesDictionary, on='Ref. Charge Code')
		
		#Filter DataFrame based on those charges
		caseType = caseType[caseType['Category']==caseCategory]

		#If DataFrame is empty, add to blank count
		if caseType.empty:
			blankCount = blankCount + 1

		#Append Filtered dataframe to list
		filteredXLS.append(caseType)

	#If 4 Empty dataframes in caseTypes, return false, otherwise return that dataframe
	if blankCount == 4:
		return False
	else:
		return filteredXLS