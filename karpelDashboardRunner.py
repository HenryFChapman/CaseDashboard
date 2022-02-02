import pandas as pd
from KarpelStarter import karpelStarter
from DefendantDemographics import defendantDemographics
from CaseDetails import caseDetails
from HelperMethods import readDataForList, combineAllCSVs, getListOfCrimeCategories, filterLargerDataFrame, getCaseYear
from DashboardMapGenerator import geocoderRunner
from DataUploaderRunner import DataUploaderRunner
from CaseHistoryCollector import caseHistoryCollector, generateCSV
from caseHistoryGenerator import generateJCPOCaseHistory 
import os 
import shutil

# Script: karpelDashboardRunner.py
# Purpose:  This is the main runner of the karpelDashboardRunner. It collects cases from the shared H-Drive, analyzes them, 
#           then uploads them to the Karpel Dashboard.
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, os, shutil
#	 Functions: KarpelStarter, DefendantDemographics, Case Details, HelperMethods, DashboardMapGenerator, DataUploaderRunner

#Step 1: Collect Most Recent Karpel Cases
print("Starting Karpel")
karpelStarter()
consolidatedCases = caseHistoryCollector()

#Get List of Crime Categories:
crimeCategoryList = getListOfCrimeCategories()

#Get List of Jail Inmates
jailInmateList = pd.read_csv("C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\Jail Dashboard\\JailInmateLibrary.csv")

#Get List of Bond Amounts
bondAmounts = pd.read_csv("C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\BondGatherer\\AllBonds.csv")

#Get File Numbers of Disposed Cases
disposedCases = pd.read_csv("AllDisposedFileNumbers.csv")

#Get File Numbers of Not Filed Cases
notFiledCases = pd.read_csv("NotFiledCases.csv")

print("reading data")
xls = readDataForList()
year = getCaseYear(xls)

#Deletes and Remakes Data For Dashboard Folder
if os.path.exists("DataForDashboard"):
	shutil.rmtree("DataForDashboard")
os.makedirs("DataForDashboard")
print("finished reading data - " + str(year))

#Loops through every Crime Category, and Conducts Analysis on Each One
for tempCaseCategory in crimeCategoryList:

	#Filters Received, Filed, and Disposed cases by that particular category
	tempXls = filterLargerDataFrame(xls, tempCaseCategory)

	#if Category is Empty, it skips it, and doesn't analyze it
	if tempXls == False:
		print("Skipping " + tempCaseCategory)
		continue

	#Prints out Case Category as an indication that it's completed
	print(tempCaseCategory)

	#Step 2: Conduct Analysis on Most Recent Karpel Cases by category (Defendant Based Analysis and Case Details)
	defendantDemographics(tempXls, tempCaseCategory, year, jailInmateList, disposedCases, notFiledCases, bondAmounts)
	caseDetails(tempXls, tempCaseCategory, year)


#Loop Through Years
listOfYears = list(set(consolidatedCases[0]["Year"].tolist()))
print(listOfYears)
chargesDictionary = pd.read_csv("HelperDatasets\\ChargeCodeCategories.csv", encoding = 'utf-8')
for year in listOfYears:

	#Loop Through Categories
	for tempCaseCategory in crimeCategoryList:

		#Merge In Case Charges
		tempCategoryDF = consolidatedCases[0].merge(chargesDictionary, on='Ref. Charge Code')
		tempCategoryDF = tempCategoryDF[tempCategoryDF['Category']==tempCaseCategory]
		tempCategoryDF = tempCategoryDF[tempCategoryDF['Year']==year]
		receivedFileNumbers = list(set(tempCategoryDF['File #'].tolist()))

		if len(receivedFileNumbers)!=0:
			generateJCPOCaseHistory(year, tempCaseCategory, receivedFileNumbers, consolidatedCases)

	#Merge In Case Charges
	tempCategoryDF = consolidatedCases[0].merge(chargesDictionary, on='Ref. Charge Code')
	tempCategoryDF = tempCategoryDF[tempCategoryDF['Year']==year]
	receivedFileNumbers = list(set(tempCategoryDF['File #'].tolist()))
	generateJCPOCaseHistory(year, "All", receivedFileNumbers, consolidatedCases)

#Step 2.5 = Run All 2021 Cases - Once it's done with each case category, it'll do all of them
defendantDemographics(xls, "All", year, jailInmateList, disposedCases, notFiledCases, bondAmounts)
caseDetails(xls, "All", year)

#Step 3: Collect All Analysis into one CSV File
print("Combining All CSVs")
combineAllCSVs(year)
generateCSV()

#Step 4: Run Geocoding Analysis (This Handles the Maping Aspect)
print("Geocoding and Preparing Maps")
geocoderRunner(xls, year)

#Step 5: Upload to ESRI Dashboard
print("Uploading Data to ESRI Online")
DataUploaderRunner()