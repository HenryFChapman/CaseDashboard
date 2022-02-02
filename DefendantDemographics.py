import pandas as pd
from datetime import datetime
from datetime import date
import datetime
import numpy as np
import os
from datetime import datetime, timedelta
from HelperMethods import getCaseType

# Script: DefendantDemographics.py
# Purpose:  This script takes in a dataframe of received, filed and disposed charges. It returns csv files for demographics of the defendants 
#			charged with those cases. 
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, datetime, numpy, os
#	 Functions: defendantRace, defendantSex, defendantAge


# Function:  defendantRace
# Purpose:   This method returns the counts of each defendant's race for each case type
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list where each element is a dataframe of case types), tempCaseCategory (string of the case type)
# Return:    No return values, but saves a CSV for each case type (robbery, homicide, etc.)
def defendantRace(xls, tempCaseCategory, year):
	
	#Initialize Blank DataFrame
	race = pd.DataFrame()

	#Initialize Counter to Progress Through List
	caseInput = 0

	#Loop Through Each Case Type (Received, Not-Filed, Filed, Disposed)
	for caseType in xls:
		#Drop Duplicate File Numbers to isolate cases, not charges
		caseType = caseType.drop_duplicates(subset=['File #'])

		#Get a string with the case type
		caseLabel = getCaseType(caseInput)

		#Get get a series of counts for each type of case
		race[caseLabel] = caseType.groupby(['Def. Race']).size()

		#increment counter for caseType by one
		caseInput = caseInput + 1
	
	#Get a Column for Each Year - It uses the current year currently
	race['Year'] = year

	#Creates a "Category" using the index of the dataframe
	race['Item'] = race.index

	#Drop the Index
	race.reset_index(drop = True, inplace=True)
	
	#Create a New Column using the category of case (Homicide, Robbery, etc.)
	race['caseCategory'] = tempCaseCategory

	#Export to .CSV in the DataForDashboard Folder
	race.to_csv("DataForDashboard\\" +tempCaseCategory+" - RaceDemographics.csv", encoding='utf-8', index=False)

# Function:  defendantSex
# Purpose:   This method returns the counts of each defendant's sex for each case type
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list where each element is a dataframe of case types), tempCaseCategory (string of the case type)
# Return:    No return values, but saves a CSV for each case type (robbery, homicide, etc.)
def defendantSex(xls, tempCaseCategory, year):

	#Initializes a Blank DataFrame
	gender = pd.DataFrame()

	#Initializes caseInput Counter
	caseInput = 0
	for caseType in xls:

		#Drops Duplicates (to get unique cases)
		caseType = caseType.drop_duplicates(subset=['File #'])

		#Get a string for the case type
		caseLabel = getCaseType(caseInput)

		#Add a new column for the case type (Received, Filed, Disposed, etc.)
		gender[caseLabel] = caseType.groupby(['Def. Sex']).size()

		#increment caseType by 1
		caseInput = caseInput + 1

	#Add a new column for the current year
	gender["Year"] = year

	#Add a column using the index (m/f/u)
	gender['Item'] = gender.index

	#drop the current index
	gender.reset_index(drop = True, inplace=True)
	
	#Add a column using the case category
	gender['caseCategory'] = tempCaseCategory
	
	#Drop unknown genders (there isn't that many of them)
	gender = gender[gender['Item'] != "U"]

	#Export a CSV for the genders of each case category
	gender.to_csv("DataForDashboard\\"+tempCaseCategory+" - GenderDemographics.csv", encoding='utf-8', index=False)

# Function:  defendantAge
# Purpose:   This method makes a histogram of defendant's ages 
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list where each element is a dataframe of case types), tempCaseCategory (string of the case type)
# Return:    No return values, but saves a CSV for each case type (robbery, homicide, etc.)
def defendantAge(xls, tempCaseCategory, year):

	#initializing blank dataframes
	age = pd.DataFrame()

	#initialize case input counter
	caseInput = 0

	#Loop through each case type
	for caseType in xls:

		#Drop duplicate file numbers to get individual cases
		caseType = caseType.drop_duplicates(subset=['File #'])

		#Drop all the null DOBs so the program doesn't crash
		caseType = caseType.dropna(subset = ['Def. DOB'])

		#Get a string for the type of case we're dealing with here
		caseLabel = getCaseType(caseInput)

		#Convert Defendant DOB to datetime
		caseType['Def. DOB'] = pd.to_datetime(caseType['Def. DOB'])

		#Convert Entry Date to datetime
		caseType['Enter Dt.'] = pd.to_datetime(caseType['Enter Dt.'])

		#Get the Age at time of referral date by subtracting Entry Date by Defendant DOB
		caseType['Age'] = caseType['Enter Dt.'] - caseType['Def. DOB']

		#Get the Age in Years by Dividing by a year
		caseType['Age'] = caseType['Age']/np.timedelta64(1, "Y")

		#Sort the values to speed up the sorting into bins
		caseType = caseType.sort_values('Age')

		#Create bins for histogram (0 to 100) - each bin is 10
		bins = np.arange(0, 110, 10)
		ind = np.digitize(caseType['Age'], bins)

		#Create a new column for each case type with ages
		age[caseLabel] = caseType['Age'].value_counts(bins=bins, sort=False)

		#Increment caseInput by 1
		caseInput = caseInput + 1

	#Add a Column with the year
	age["Year"] = year

	#Add a column using the index
	age['Item'] = age.index

	#Drop the index
	age.reset_index(drop = True, inplace=True)
	
	#Add a column with the category of cases (robbery, homicide, etc.)
	age['caseCategory'] = tempCaseCategory

	#Export a CSV with the temp case type
	age.to_csv("DataForDashboard\\" +tempCaseCategory+" - AgeDemographics.csv", encoding='utf-8', index=False)


def defendantBond(xls, tempCaseCategory, year, bondAmounts):

	#initializing blank dataframes
	bond = pd.DataFrame()

	#initialize case input counter
	caseInput = 0

	#Loop through each case type
	for caseType in xls:

		#Drop duplicate file numbers to get individual cases
		caseType = caseType.drop_duplicates(subset=['File #'])

		caseType = caseType.merge(bondAmounts, on = 'File #', how = 'left')

		#Drop all the null DOBs so the program doesn't crash
		caseType = caseType.dropna(subset = ['Initial Bond'])

		#Get a string for the type of case we're dealing with here
		caseLabel = getCaseType(caseInput)

		#Sort the values to speed up the sorting into bins
		caseType = caseType.sort_values('Initial Bond')

		caseType['Initial Bond'] = caseType['Initial Bond']/1000
		#Create bins for histogram (0 to 100) - each bin is 10
		bins = np.arange(0, 200, 15)
		ind = np.digitize(caseType['Initial Bond'], bins)

		#Create a new column for each case type with ages
		bond[caseLabel] = caseType['Initial Bond'].value_counts(bins=bins, sort=False)

		#Increment caseInput by 1
		caseInput = caseInput + 1

	#Add a Column with the year
	bond["Year"] = year

	#Add a column using the index
	bond['Item'] = bond.index

	#Drop the index
	bond.reset_index(drop = True, inplace=True)
	
	#Add a column with the category of cases (robbery, homicide, etc.)
	bond['caseCategory'] = tempCaseCategory

	#Export a CSV with the temp case type
	bond.to_csv("DataForDashboard\\" +tempCaseCategory+" - Bonds.csv", encoding='utf-8', index=False)
	
def defendantIncarcerated(xls, tempCaseCategory, year, jailInmateList, disposedCases, notFiledCases):

	#Initializes blank list of data
	listOfData = []

	#case numbers
	caseNumbers = []

	#initialize case input counter
	caseInput = 0

	#Loop through each case type
	for caseType in xls:

		#Drop duplicate file numbers to get individual cases
		caseType = caseType.drop_duplicates(subset=['File #'])

		#Get a string for the type of case we're dealing with here
		caseLabel = getCaseType(caseInput)

		#Drop duplicate file numbers to get individual cases
		caseType = caseType.merge(jailInmateList, on = "File #", how = 'left')

		caseType = caseType[~caseType['File #'].isin(disposedCases['File #'].tolist())]
		caseType = caseType[~caseType['File #'].isin(notFiledCases['File #'].tolist())]


		tempCaseNumber = len(caseType.index)

		caseType = caseType.drop_duplicates(subset = ['InmateNum'])
		caseType = caseType.dropna(subset = ['InmateNum'])

		tempIncarceratedNumber = len(caseType.index)

		if tempCaseNumber == 0:
			incarceratingPercentage = 0 
		else:
			incarceratingPercentage = tempIncarceratedNumber / tempCaseNumber

		#append a string to list using the casetype label and the number of cases
		listOfData.append(getCaseType(caseInput) + " " + str(incarceratingPercentage))
		caseNumbers.append(tempCaseNumber)

		#Increment case input by one
		caseInput = caseInput + 1

	#initialize dataframe for incarceratedByYear
	incarceratedByYear = pd.DataFrame(listOfData, columns=['Data'])

	#Split the column by spaces
	incarceratedByYear = incarceratedByYear['Data'].str.split(' ', 3, expand=True)
	
	#initialize a new year column
	incarceratedByYear["Year"] = year

	#Rename columns into type, count, and year
	incarceratedByYear = incarceratedByYear.rename(columns={0: "Type", 1:"Count", 2:"Year"})

	#Pivot the table to get the data into the correct format
	incarceratedByYear = incarceratedByYear.reset_index().pivot('Type', 'Year', 'Count')

	#create a list of columns
	columns = incarceratedByYear.columns.tolist()
	
	#reset the index of the case numbers dataframe
	incarceratedByYear.reset_index(inplace=True)

	#Transpose the caseNumbersByYear dataframe
	incarceratedByYear = incarceratedByYear.set_index('Type').T
	
	#Create a new column for item using the previous columns list
	incarceratedByYear['Item'] = columns

	#Create a new column for the year
	incarceratedByYear['Year'] = year

	#Create a new column for year
	col = incarceratedByYear.pop("Year")
	
	#Insert that column into dataframe
	incarceratedByYear.insert(0, col.name, col)
	
	#Create a new column for case category
	incarceratedByYear['caseCategory'] = tempCaseCategory

	incarceratedByYear['Disposed'] = caseNumbers[0]

	#Export Dataframe to CSV
	incarceratedByYear.to_csv("DataForDashboard\\"+tempCaseCategory+" - incarceratedByYear.csv", encoding='utf-8', index=False)

#This is the Main Method
def defendantDemographics(xls, tempCaseCategory, year, jailInmateList, disposedCases, notFiledCases, bondAmounts):
	defendantRace(xls, tempCaseCategory, year)
	defendantSex(xls, tempCaseCategory, year)
	defendantAge(xls, tempCaseCategory, year)
	defendantIncarcerated(xls, tempCaseCategory, year, jailInmateList, disposedCases, notFiledCases)
	defendantBond(xls, tempCaseCategory, year, bondAmounts)