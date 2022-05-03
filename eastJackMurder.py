import pandas as pd 


#headers
headers = pd.read_excel("chargeCodeHeaders.xlsx")

#Charge Codes
chargeCodes = pd.read_csv("https://www.mshp.dps.missouri.gov/MSHPWeb/PatrolDivisions/CRID/ChargeCodeCSV2022-1-28.csv", sep = ",", names=headers['Columns'].tolist())


#Disposed Cases
path = r'C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Karpel Dashboard - v2.0\RawDataConsolidated\3 - Disposed.csv'
disposedCases = pd.read_csv(path)

#print(disposedCases)

disposedCases = disposedCases.merge(chargeCodes, on='Ref. Charge Code', how = 'left')

disposedCases = disposedCases[(disposedCases['Agency'] != 2) & (disposedCases['NCIC Category']==9)]

disposedCases.to_excel("disposedCases.xlsx")