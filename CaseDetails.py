import pandas as pd
from datetime import datetime
from datetime import date
from datetime import datetime, timedelta
from HelperMethods import getCaseType
import numpy as np
import os

# Script:   CaseDetails.py
# Purpose:  This script performs analysis on filtered dataframes. It conducts analysis by case numbers, agency, and numbers. It also collects statistics on trial outcomes.
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, os, numpy, and datetime
#	 Functions: getCaseType

# Function:  agency
# Purpose:   Counts a list of police agencies by case category
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
# Return:    No Return Value
def agency(xls, tempCaseCategory, year):
	#Initialize Blank DataFrame for referring agencies
	referringAgency = pd.DataFrame()
	
	#Read Dictionary of Referring Police Agencies
	PDAgency = pd.read_csv("HelperDatasets\\PD Agency.csv", encoding = 'utf-8')
	
	#Convert Agency Labels as Integers for Matching
	PDAgency['Agency'] = PDAgency['Agency'].astype(int)
	
	#Initialize caseInput Variable as 0
	caseInput = 0

	#Loop through each caseType (Received, not-filed, filed, disposed)
	for caseType in xls:

		#Drop all the na values (Cases that don't have a listed agency)
		caseType = caseType.dropna(subset=['Agency'])

		#Drop all the duplicate file numbers (this counts unique cases, not charges)
		caseType = caseType.drop_duplicates(subset = ['File #'])

		#Converts Agency into an integer (for merging later on)
		caseType['Agency'] = caseType['Agency'].astype(int)
		
		#Gets a string label for caseType
		caseLabel = getCaseType(caseInput)

		#Merge in Agency Names
		caseType = caseType.merge(PDAgency, on='Agency')
		
		#Count Agency Names by numbers
		referringAgency[caseLabel] = caseType.groupby(['PD NAME']).size()
		
		#Increment caseInput by 1
		caseInput = caseInput + 1

	#Create a new column with the temporary year
	referringAgency["Year"] = year
	
	#Create a New Column using the referring agency's index
	referringAgency['Item'] = referringAgency.index

	#Reset Index
	referringAgency.reset_index(drop = True, inplace=True)
	
	#Create a new column wih the case category
	referringAgency['caseCategory'] = tempCaseCategory
	
	#Export a new CSV with case category and agency
	referringAgency.to_csv("DataForDashboard\\" + tempCaseCategory + " - ReferringAgencies.csv", encoding='utf-8', index=False)

# Function:  caseNumbers
# Purpose:   generates a list of caseNumbers by case category
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
# Return:    No Return Value
def caseNumbers(xls, tempCaseCategory, year):
	#Initializes blank list of data
	listOfData = []
	
	#Initialize caseInput Variable as 0
	caseInput = 0

	#Loop through each caseType (Received, not-filed, filed, disposed)
	for caseType in xls:
		#Drop Duplicates to get unique cases
		caseType = caseType.drop_duplicates(subset = ['File #'])

		#append a string to list using the casetype label and the number of cases
		listOfData.append(getCaseType(caseInput) + " " + str(len(caseType.index)))
		
		#Increment case input by one
		caseInput = caseInput + 1

	#initialize dataframe for caseNumbersByYear
	caseNumbersByYear = pd.DataFrame(listOfData, columns=['Data'])
	
	#Split the column by spaces
	caseNumbersByYear = caseNumbersByYear['Data'].str.split(' ', 3, expand=True)
	
	#initialize a new year column
	caseNumbersByYear["Year"] = year

	#Rename columns into type, count, and year
	caseNumbersByYear = caseNumbersByYear.rename(columns={0: "Type", 1:"Count", 2:"Year"})

	#Pivot the table to get the data into the correct format
	caseNumbersByYear = caseNumbersByYear.reset_index().pivot('Type', 'Year', 'Count')

	#create a list of columns
	columns = caseNumbersByYear.columns.tolist()
	
	#reset the index of the case numbers dataframe
	caseNumbersByYear.reset_index(inplace=True)

	#Transpose the caseNumbersByYear dataframe
	caseNumbersByYear = caseNumbersByYear.set_index('Type').T
	
	#Create a new column for item using the previous columns list
	caseNumbersByYear['Item'] = columns

	#Create a new column for the year
	caseNumbersByYear['Year'] = year

	#Create a new column for year
	col = caseNumbersByYear.pop("Year")
	
	#Insert that column into dataframe
	caseNumbersByYear.insert(0, col.name, col)
	
	#Create a new column for case category
	caseNumbersByYear['caseCategory'] = tempCaseCategory

	#Export Dataframe to CSV
	caseNumbersByYear.to_csv("DataForDashboard\\"+tempCaseCategory+" - CasesByYear.csv", encoding='utf-8', index=False)

# Function:  trialCase
# Purpose:   Function determines if a disposed case went to trial or not
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Trial Case" or "Not Trial Case"
def trialCase(dataframe):

	#Filters DataFrame by "Trial"
	dataframe = dataframe[dataframe['Activity']=='Trial']

	#If Activity contains trial at all, then the case went to trial, return "Trial Case"
	if dataframe['Activity'].str.contains('Trial').any() == True:
		return "Trial Case"
	else:
		return "Not Trial Case"

# Function:  guiltyVerdict
# Purpose:   Function determines if a case has a guilty trial verdict
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Guilty" or "Not Guilty"
def guiltyVerdict(dataframe):

	#Filters dataframe by "Guilty" reasons for verdicts
	dataframe = dataframe[dataframe['Reason']=='Guilty']

	#If Reasons contains the word guilty, then it's a guilty verdict
	if dataframe['Reason'].str.contains('Guilty').any() == True:
		return "Guilty"
	else:
		return "Not Guilty"

# Function:  guiltyPlea
# Purpose:   Function determines if a case has a guilty plea
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Guilty Plea" or "Not Guilty Plea"
def guiltyPlea(dataframe):
	if dataframe['Activity'].str.contains("Guilty Plea").any() == True:
		return "Guilty Plea"
	return "Not Guilty Plea"

# Function:  drugCourt
# Purpose:   Function determines if a case has a drug court outcome
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Drug Court" or "Not Drug Court"
def drugCourt(dataframe):
	if dataframe['Activity'].str.contains("Drug Court").any() == True:
		return "Drug Court"
	return "Not Drug Court"

# Function:  entireCaseDismissal
# Purpose:   Function determines if a case was dismissed
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Entire Case Dismissed" or "Case Not Dismissed"
def entireCaseDismissal(dataframe):
	if dataframe['Reason'].str.contains("Entire Dismissal").any() == True:
		return "Entire Case Dismissed"
	return "Case Not Dismissed"

# Function:  outsideReferral
# Purpose:   Function determines if a case was dismissed
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "Referred to Other Agency" or "Not Referred to Other Agency"
def outsideReferral(dataframe):
	if dataframe['Activity'].str.contains("Outside Referral").any() == True:
		return "Referred to Other Agency"
	return "Not Referred to Other Agency"

# Function:  noProsecutionReason
# Purpose:   Function determines if a case was Not Prosecuted
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: dataframe (of disposed cases)
# Return:    String - "No Prosecution" or "None"
def noProsecutionReason(dataframe):
	if dataframe['Activity'].str.contains("No Prosecution").any() == True:
		return "No Prosecution"
	return "None"

# Function:  disposalCategories
# Purpose:   This function determines outcomes for each case. It uses a ranking algorithm to first determine trial cases, then cases that didn't go to trial. 
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
# Return:    No Return Values
def disposalCategories(xls, tempCaseCategory, year):
	#Looking at just disposed cases here, so we're filtering xls by the third element (disposed cases)
	caseType = xls[3]

	#Reading the Disposition Codes as a dictionary
	disposalCodes = pd.read_csv("HelperDatasets\\Disposition Codes.csv", encoding = 'utf-8')
	
	#This Bit Handles The Outcome Part of the Code
	#Initializes DataFrames
	trialCasesVSNonTrialCases = pd.DataFrame()
	trialOutcomes = pd.DataFrame()
	nonTrialOutcomes = pd.DataFrame()
	tempYearTrial = pd.DataFrame()
	tempYearTrialVerdict = pd.DataFrame()
	tempYearNoTrialVerdict = pd.DataFrame()

	#Merge In Disposal Codes into Disposed Cases
	caseType = pd.merge(caseType, disposalCodes, on ='Disp. Code', how ='left')

	#Initialises Strings for Disposed and Year for later use
	caseLabel = "Disposed"
	yearText = year

	#Initializes Lists for Later Analysis
	trialFileNumbers = []
	caseTrial = []
	trialGuilt = []
	nonTrialFileNumbers = []
	nonTrialGuilt = []
	nonTrialStatus = []
		
	#Generates a list of unique file numbers
	justFileNumbers = list(set(caseType['File #'].tolist()))
	
	#Creates a column for unique file numbers in the tempYear trial dataframe
	tempYearTrial['File #'] = justFileNumbers
		
	#Loops through File Numbers
	for fileNumber in justFileNumbers:
		
		#Let's Look at Just One Case
		indCaseCharges = caseType[caseType['File #'] == fileNumber]
		
		#Appending the trial status of that one case to the caseTrial List
		caseTrial.append(trialCase(indCaseCharges))

		#First Look at Whether There's a Trial Verdict
		if trialCase(indCaseCharges) == "Trial Case":
			trialFileNumbers.append(fileNumber)
			trialGuilt.append(guiltyVerdict(indCaseCharges))

		#If There's No Trial Verdict
		elif trialCase(indCaseCharges) != "Trial Case":
			nonTrialFileNumbers.append(fileNumber)

			#Check Guilty Plea
			if guiltyPlea(indCaseCharges) == "Guilty Plea":
				nonTrialStatus.append("Guilty Plea")

			#Check Drug Court
			elif drugCourt(indCaseCharges) == "Drug Court":
				nonTrialStatus.append("Drug Court")

			#Check Case Dismissal
			elif entireCaseDismissal(indCaseCharges) == "Entire Case Dismissed":
				nonTrialStatus.append("Entire Case Dismissed")

			#Check Outside Referral
			elif outsideReferral(indCaseCharges) == "Referred to Other Agency":
				nonTrialStatus.append("Referred to Other Agency")

			#Check No Prosecution Reasons
			elif noProsecutionReason(indCaseCharges) == "No Prosecution":
				nonTrialStatus.append("No Prosecution")
			else:
				nonTrialStatus.append("Other")

	#Constructing DataFrame Based on Whether Case Went To Trial (Trial/No Trial)
	tempYearTrial['Status'] = caseTrial

	if tempCaseCategory == "All":
		tempYearTrial['Year'] = year
		tempYearTrial.to_csv(str(year) + "Trial File Numbers.csv")

	#Constructing DataFrame Based on Trial Verdicts (Guilty/Not Guilty)
	tempYearTrialVerdict['File #'] = trialFileNumbers
	tempYearTrialVerdict['Status'] = trialGuilt

	#Constructing DataFrame Based on Non-Trial Verdicts (Plea/Drug Court/Dismissal)
	tempYearNoTrialVerdict['File #'] = nonTrialFileNumbers
	tempYearNoTrialVerdict['Status'] = nonTrialStatus

	trialCasesVSNonTrialCases[caseLabel] = tempYearTrial.groupby(['Status']).size()
	trialOutcomes[caseLabel] = tempYearTrialVerdict.groupby(['Status']).size()
	nonTrialOutcomes[caseLabel] = tempYearNoTrialVerdict.groupby(['Status']).size()
	
	#Whether Case Went to Trial
	trialCasesVSNonTrialCases["Year"] = year
	trialCasesVSNonTrialCases['Item'] = trialCasesVSNonTrialCases.index
	trialCasesVSNonTrialCases['Received'] = 0
	trialCasesVSNonTrialCases['Not-Filed'] = 0
	trialCasesVSNonTrialCases['Filed'] = 0
	trialCasesVSNonTrialCases.reset_index(drop = True, inplace=True)
	trialCasesVSNonTrialCases['caseCategory'] = tempCaseCategory
	trialCasesVSNonTrialCases.to_csv("DataForDashboard\\"+tempCaseCategory+" - TrialCases.csv", encoding='utf-8', index=False)

	#What Kind of Guilty Verdict They Had At Trial
	trialOutcomes["Year"] = year
	trialOutcomes['Item'] = trialOutcomes.index
	trialOutcomes['Received'] = 0
	trialOutcomes['Not-Filed'] = 0
	trialOutcomes['Filed'] = 0
	trialOutcomes.reset_index(drop = True, inplace=True)
	trialOutcomes['caseCategory'] = tempCaseCategory
	trialOutcomes.to_csv("DataForDashboard\\"+tempCaseCategory+" - TrialOutcomes.csv", encoding='utf-8', index=False)

	#What Kind of Outcomes They Had Outside of Trial
	nonTrialOutcomes["Year"] = year
	nonTrialOutcomes['Item'] = nonTrialOutcomes.index
	nonTrialOutcomes['Received'] = 0
	nonTrialOutcomes['Not-Filed'] = 0
	nonTrialOutcomes['Filed'] = 0
	nonTrialOutcomes.reset_index(drop = True, inplace=True)
	nonTrialOutcomes['caseCategory'] = tempCaseCategory
	nonTrialOutcomes.to_csv("DataForDashboard\\"+tempCaseCategory+" - NonTrialOutcomes.csv", encoding='utf-8', index=False)

# Function:  disposalDateHistogram
# Purpose:   This function generates a histogram that calculates how long it takes to dispose a case in Jackson County (in months)
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
# Return:    No Return Values
def disposalDateHistogram(xls, tempCaseCategory, year):
	
	#Looking at just disposed cases here, so we're filtering xls by the third element (disposed cases)
	caseType = xls[3]
	
	#Initializes a DataFrame
	age = pd.DataFrame()

	#This Bit Handles the Time Outcome of the Code
	caseLabel = "Disposed"

	#Drops Case Duplicates
	caseType = caseType.drop_duplicates(subset=['File #'])
	caseType = caseType.reset_index()

	#Converts to DateTime and Generates a time in months
	caseType['Enter Dt.'] = pd.to_datetime(caseType['Enter Dt.'])
	caseType['Disp. Dt.'] = pd.to_datetime(caseType['Disp. Dt.'])
	caseType['Age of Case (Months)'] = caseType['Disp. Dt.'] - caseType['Enter Dt.']
	caseType['Age of Case (Months)'] = caseType['Age of Case (Months)']/np.timedelta64(1, "M")

	#Sorts Values for Easier Histogram Generation
	caseType = caseType.sort_values('Age of Case (Months)')

	#Uses Bins to sort numbers into a histogram
	bins = np.arange(0, 110, 10)
	ind = np.digitize(caseType['Age of Case (Months)'], bins)
	age[caseLabel] = caseType['Age of Case (Months)'].value_counts(bins=bins, sort=False)

	#Adds Dummy Labels for Later Concatenation
	age["Year"] = year
	age['Item'] = age.index
	age['Received'] = 0
	age['Not-Filed'] = 0
	age['Filed'] = 0

	#Reset Index and generates CSV File
	age.reset_index(drop = True, inplace=True)
	age['caseCategory'] = tempCaseCategory
	age.to_csv("DataForDashboard\\" + tempCaseCategory + " - AgeOfCase.csv", encoding='utf-8', index=False)

# Function:  refusalDateHistogram
# Purpose:   This function generates a histogram that calculates how long it takes to decline a case in Jackson County (in months)
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
# Return:    No Return Values
def refusalDateHistogram(xls, tempCaseCategory, year):
	
	#Looking at just declined cases here, so we're filtering xls by the second element (disposed cases)
	caseType = xls[1]

	#Initializing DataFrame
	age = pd.DataFrame()

	#This Bit Handles the Time Outcome of the Code
	caseLabel = "Not-Filed"

	#Drop Duplicates to Get Unique Cases
	caseType = caseType.drop_duplicates(subset=['File #'])
	caseType = caseType.reset_index(drop= True)

	#This Bit Handles the Time Conversion
	caseType['Enter Dt.'] = pd.to_datetime(caseType['Enter Dt.'])
	caseType['Disp. Dt.'] = pd.to_datetime(caseType['Disp. Dt.'])
	caseType = caseType.reset_index(drop = True)
	caseType['Age of Case (Months)'] = caseType['Disp. Dt.'] - caseType['Enter Dt.']
	caseType['Age of Case (Months)'] = caseType['Age of Case (Months)']/np.timedelta64(1, "M")

	#Sort Values for the Histogram, then sort thingss into bins
	caseType = caseType.sort_values('Age of Case (Months)')
	bins = np.arange(0, 110, 10)
	ind = np.digitize(caseType['Age of Case (Months)'], bins)
	age[caseLabel] = caseType['Age of Case (Months)'].value_counts(bins=bins, sort=False)

	#Create Dummy Variables for the Concatenation Process
	age["Year"] = year
	age['Item'] = age.index
	age['Received'] = 0
	age['Filed'] = 0
	age['Disposed'] = 0

	#Export DataFrame with the Histogram
	age.reset_index(drop = True, inplace=True)
	age['caseCategory'] = tempCaseCategory
	age.to_csv("DataForDashboard\\" + tempCaseCategory + " - DeclinedAgeOfCase.csv", encoding='utf-8', index=False)


# Function:  refusalReasons
# Purpose:   This function generates a dataframe that shows why cases were declined
# Author:    Henry Chapman, hchapman@jacksongov.org
# Arguments: xls (list of received, not-filed, filed, and disposed cases), tempCaseCategory (string label of case category), year (integer) of year of analysis
def refusalReasons(xls, tempCaseCategory, year):
	#Initialize Blank DataFrames
	declineReasons = pd.DataFrame()

	#Isoalte Just Declined Cases
	caseType = xls[1]

	#Load Refusal Reasons
	refusalReasonsDataSet = pd.read_csv("HelperDatasets\\RefusalReasons.csv", encoding = 'utf-8')

	#Drop NA - Those without a disposal code
	caseType = caseType.dropna(subset = ['Disp. Code'])
	
	#Drop Duplicate Rows - This gives us unique disposal reasons by case
	caseType = caseType.drop_duplicates()
	
	#Get the Case Label for Declined Cases
	caseLabel = getCaseType(1)
	
	#Merge In the Disposal Reason
	caseType = caseType.merge(refusalReasonsDataSet, on = 'Disp. Code')
	
	#GroupBy Disposal Reasons, then add it to our new export dataframe
	declineReasons[caseLabel] = caseType.groupby(['Reason']).size()

	#Create Dummy Columns, then export the dataframe
	declineReasons['Year'] = year
	declineReasons['Item'] = declineReasons.index
	declineReasons['Received'] = 0
	declineReasons['Filed'] = 0
	declineReasons['Disposed'] = 0
	declineReasons.reset_index(drop = True, inplace=True)
	declineReasons['caseCategory'] = tempCaseCategory

	declineReasons.to_csv("DataForDashboard\\" + tempCaseCategory + " - DeclineReasons.csv", encoding='utf-8', index=False)


def attorneys(xls, tempCaseCategory, year):

	#Initialize Blank DataFrames
	#attorneyDataFrame = pd.DataFrame()

	#GroupBy Disposal Reasons, then add it to our new export dataframe
	#declineReasons[caseLabel] = caseType.groupby(['Assigned Atty']).size()

	#Initialize Blank DataFrame for referring agencies
	attorneyDataFrame = pd.DataFrame()

	#Initialize caseInput Variable as 0
	caseInput = 0

	#Loop through each caseType (Received, not-filed, filed, disposed)
	for caseType in xls:

		#Drop all the na values (Cases that don't have a listed agency)
		caseType = caseType.dropna(subset=['Assigned Atty'])

		#Drop all the duplicate file numbers (this counts unique cases, not charges)
		caseType = caseType.drop_duplicates(subset = ['File #'])
		
		#Gets a string label for caseType
		caseLabel = getCaseType(caseInput)

		#Count Agency Names by numbers
		attorneyDataFrame[caseLabel] = caseType.groupby(['Assigned Atty']).size()
		
		#Increment caseInput by 1
		caseInput = caseInput + 1

	#Create a new column with the temporary year
	attorneyDataFrame["Year"] = year
	
	#Create a New Column using the referring agency's index
	attorneyDataFrame['Item'] = attorneyDataFrame.index

	#Reset Index
	attorneyDataFrame.reset_index(drop = True, inplace=True)
	
	#Create a new column wih the case category
	attorneyDataFrame['caseCategory'] = tempCaseCategory
	
	#Export a new CSV with case category and agency
	attorneyDataFrame.to_csv("DataForDashboard\\" + tempCaseCategory + " - Attorney.csv", encoding='utf-8', index=False)

#Main Function that Runs all the case analysis portions. Called from KarpelDashboardRunner Function
def caseDetails(xls, tempCaseCategory, year):
	agency(xls, tempCaseCategory, year)
	caseNumbers(xls, tempCaseCategory, year)
	disposalCategories(xls, tempCaseCategory, year)
	disposalDateHistogram(xls, tempCaseCategory, year)
	refusalDateHistogram(xls, tempCaseCategory, year)
	refusalReasons(xls, tempCaseCategory, year)
	#attorneys(xls, tempCaseCategory, year)
