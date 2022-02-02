import pandas as pd
from HelperMethods import getUniqueListOfFiledCases
import os

# Script:   karpelStarter.py
# Purpose:  This script retrieves the most recent cases that are extracted from Karpel via daily data query.
#           It  cleans the data set, then returns it for analysis.
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, os,
#	 Functions: None

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

# Function:  loadMostRecentFile
# Purpose:   This loads the most recent 2021 cases out of Karpel from the WeeklyUpload folder on the H Drive.
#            It renames columns so they are all standard accross the three types of case categories.
#            It also consolidates every address column into one column (Street Address, Town, ZipCode)
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: newestFile, weeklyUpload
# Return:    Returns a list of 3 dataframes (Received Cases, Filed Cases, Disposed Cases)
def loadMostRecentFile(newestFile, weeklyUpload):

	#Loads Weekly Upload Folder
	directoryList = os.listdir(weeklyUpload)

	#Sorts Folder So Newest Are Up Front
	directoryList.sort(reverse=True)

	i = 0
	updatedCompleteDFs = []

	#Loads Spreadsheet to Fix Misspelled Column Labels
	fixedRowlabels = pd.ExcelFile('HelperDatasets\\FixedRowLabels.xlsx')

	#Loops Through Weekly Upload Directory
	for item in directoryList:

		#Checking if it's the most recent file (Received,Disposed,Filed)
		if newestFile in item and ("_1800" in item) and ("CaseNo" not in item):

			#print(newestFile)
			#if "CaseNo" in newestFile:
			#	continue

			#Load the Most Recent File as a DataFrame
			tempUpdatedDF = pd.read_csv(weeklyUpload + item)

			#Fix the Misspelled/Incorrect Column Headers/Standardize Column Headers
			fixedRowLabel = pd.read_excel(fixedRowlabels, sheet_name = fixedRowlabels.sheet_names[i])
			fixedRowLabelDict = pd.Series(fixedRowLabel['New Name'].values,index=fixedRowLabel['Original Name']).to_dict()
			tempUpdatedDF = tempUpdatedDF.rename(columns=fixedRowLabelDict)

			#Concatenates Address Field into One Field, and drops the old fields that we don't need. 
			tempUpdatedDF["Def. Street Address"] = tempUpdatedDF["Def. Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Street Address2"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. City"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. State"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Zipcode"].fillna('').astype(str)
			tempUpdatedDF["Offense Street Address"] = tempUpdatedDF["Offense Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense Street Address 2"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense City"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense State"].fillna('').astype(str) + ", " + tempUpdatedDF["Off. Zipcode"].fillna('').astype(str)
			tempUpdatedDF = tempUpdatedDF.drop(columns=["Def. Street Address2", "Def. City", "Def. State", "Def. Zipcode", "Offense Street Address 2", "Offense City", "Offense State", "Off. Zipcode", "Def. SSN"])

			updatedCompleteDFs.append(tempUpdatedDF)
			i = i + 1
	return updatedCompleteDFs


# Function:  cleanDataset
# Purpose:   This Performs Basic Cleanings and Filters the Data so we just get 2021 data.
#            It filters just 2021 cases (by date and file number). It also removes anyone named "Bogus" or "Test"
#            Finally, it saves the 2021 cases in a the RawData folder. It saves a CSV for Received, Filed, and Disposed Cases
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: newestFile, weeklyUpload
# Return:    None
def cleanDataSet(updatedCompleteDFs, uniqueFiledCRNs):

	#List of File Names in RawData
	fileNames = os.listdir("RawData")

	disposedCases = []
	notFiledCases = []

	i = 0
	for caseType in updatedCompleteDFs:
		#Drop All the Defendants Named Bogus/Test
		caseTypeClean = caseType[~caseType['Def. Name'].str.contains("Bogus")]
		caseTypeClean = caseTypeClean[~caseTypeClean['Def. Name'].str.contains("Bogus", na=False)]
		caseTypeClean = caseTypeClean[~caseTypeClean['Def. Name'].str.contains("Test", na=False)]
		caseTypeClean = caseTypeClean.reset_index()
		
		#If it's a received case, it filters by only 2021 file numbers
		if '1 - Received' in fileNames[i]:
			caseTypeClean['Referral Date'] = pd.to_datetime(caseTypeClean["Referral Date"])
			caseTypeClean = caseTypeClean[(caseTypeClean['Referral Date'] > '2022-1-1')]
			caseTypeClean['Year'] = caseTypeClean['Referral Date'].dt.year

		#If it's a not filed case, we only want not filed cases with a 2021 not-filed date
		if '2 - Not Filed' in fileNames[i]:
			caseTypeClean["Disp. Dt."] = pd.to_datetime(caseTypeClean["Disp. Dt."])
			caseTypeClean = caseTypeClean[~caseTypeClean['File #'].isin(uniqueFiledCRNs)]
			caseTypeClean = caseTypeClean[(caseTypeClean['Disp. Dt.'] > '2022-1-1')]
			caseTypeClean['Year'] = caseTypeClean['Disp. Dt.'].dt.year
			notFiledCases.append(caseTypeClean)

		#If it's a filed case, we only look at cases that have a 2021 file date
		if '3 - Filed' in fileNames[i]:
			caseTypeClean["Filing Dt."] = pd.to_datetime(caseTypeClean["Filing Dt."])
			caseTypeClean = caseTypeClean[(caseTypeClean['Filing Dt.'] > '2022-1-1')]
			caseTypeClean['Year'] = caseTypeClean['Filing Dt.'].dt.year

		if '4 - Disposed' in fileNames[i]:
			caseTypeClean["Disp. Dt."] = pd.to_datetime(caseTypeClean["Disp. Dt."])
			caseTypeClean = caseTypeClean[(caseTypeClean['Disp. Dt.'] > '2022-1-1')]
			caseTypeClean['Year'] = caseTypeClean['Disp. Dt.'].dt.year
			disposedCases.append(caseTypeClean)

		#Updates File Names 
		caseTypeClean.to_csv("RawData\\" + fileNames[i], index = False)

		#Increment File Name Counter by One
		i = i + 1

	disposedCases = pd.concat(disposedCases)
	disposedCases = disposedCases[['File #']]
	disposedCases = disposedCases.drop_duplicates(subset = ["File #"])
	disposedCases.to_csv("AllDisposedFileNumbers.csv")

	notFiledCases = pd.concat(notFiledCases)
	notFiledCases = notFiledCases[['File #']]
	notFiledCases = notFiledCases.drop_duplicates(subset = ["File #"])
	notFiledCases.to_csv("NotFiledCases.csv")

# Function:  karpelStarter
# Purpose:   This is the main runner of Karpel Starter. It grabs the most recent data, cleans it, then saves it.
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: None
# Return:    None
def karpelStarter():

	#FilePath of Weekly Updating Cases
	weeklyUpload = "H:\\Units Attorneys and Staff\\01 - Units\\DT Crime Strategies Unit\\Weekly Update\\"
	uniqueFiledCRNs = getUniqueListOfFiledCases(weeklyUpload)
	
	#Get Newly Updated Karpel Data from H Drive
	updatedCompleteDFs = loadMostRecentFile(getNewestFile(weeklyUpload), weeklyUpload)

	#Cleaned and Saved Dataset
	cleanDataSet(updatedCompleteDFs, uniqueFiledCRNs)


