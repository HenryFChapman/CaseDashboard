import pandas as pd 

receivedCases = "RawData\\1 - Received Charges.csv"
caseCategories = "HelperDatasets\\ChargeCodeCategories.csv"

receivedCases = pd.read_csv(receivedCases)
caseCategories = pd.read_csv(caseCategories)

receivedCases = receivedCases.merge(caseCategories, on = 'Ref. Charge Code', how = 'left')

fileNumbers = list(set(receivedCases['File #'].tolist()))

drugFileNumbers = set()

for fileNumber in fileNumbers:
	tempReceivedCase = receivedCases[receivedCases['File #']==fileNumber]

	tempCategoryList = tempReceivedCase['Category'].tolist()

	if tempCategoryList[0] != "Drugs":
		continue
	else:
		drugFileNumbers.add(fileNumber)

receivedCases = receivedCases[receivedCases['Agency']==2]
receivedCases = receivedCases[receivedCases['Category']=='Drugs']

receivedCases['Received Date'] = pd.to_datetime(receivedCases['Received Date'])

receivedCases = receivedCases[receivedCases['Received Date']>="4/1/2021"]

receivedCases[receivedCases['File #'].isin(list(drugFileNumbers))]

receivedCases.to_csv("DrugReferrals.csv")