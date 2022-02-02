import pandas as pd
import numpy as np
import plotly.graph_objects as go


def disposedCaseCounter(fnList, disposedCaseDF):

    #Here we're trying to get one disposition reason per disposed case
    #Here's the prioritization of disposed cases
        #1. Trial
        #2. Guilty Plea
        #3. No Prosecution

    fnList = list(set(fnList))
    dispositionReasons = []

    for tempFN in fnList:

        justThatCase = disposedCaseDF[disposedCaseDF['File #'] == tempFN]

        if "Trial" in justThatCase["Activity"].tolist():
            dispositionReasons.append("Trial")
        elif "Guilty Plea" in justThatCase['Activity'].tolist():
            dispositionReasons.append("Guilty Plea")
        elif "Drug Court" in justThatCase['Activity'].tolist():
            dispositionReasons.append("Drug Court")
        elif "Entire Dismissal" in justThatCase['Activity'].tolist():
            dispositionReasons.append("Entire Dismissal")
        elif "No Prosecution" in justThatCase['Activity'].tolist():
            dispositionReasons.append("No Prosecution")
        else:
            dispositionReasons.append("Other")

    dispositionReasonDF = pd.DataFrame()
    dispositionReasonDF['File #'] = fnList
    dispositionReasonDF['Disp. Reason'] = dispositionReasons
    dispositionReasonDF = dispositionReasonDF.groupby('Disp. Reason').size().to_frame().reset_index()
    dispositionReasonDF['source'] = 'C - Cases Disposed'
    dispositionReasonDF = dispositionReasonDF.rename(columns={0: 'value'})
    dispositionReasonDF['target'] = "D - " + dispositionReasonDF['Disp. Reason']
    dispositionReasonDF = dispositionReasonDF[['source', 'target', 'value']]
    return dispositionReasonDF


def declinedCaseCounter(fnList, declinedCaseDF):

    #print(declinedCaseDF.columns)

    #Here we're trying to get one disposition reason per declined case
    #Here's the prioritization of declined cases
        #1. Pending Further Investigation
        #2. Other Case Pending
        #3. Evidence Issues
        #Self Defense
        #Suspect Deceased

        #4. Lack of Evidence
        #5. Other Case
        #Last. Other
        #2. Guilty Plea
        #3. No Prosecution

    fnList = list(set(fnList))
    declineReasons = []

    for tempFN in fnList:

        justThatCase = declinedCaseDF[declinedCaseDF['File #'] == tempFN]

        if "Pending Further Investigation" in justThatCase["Activity"].tolist():
            declineReasons.append("Pending Further Investigation")
        elif ("Lack of Evidence" in justThatCase['Activity'].tolist()) or ("Evidence Issues" in justThatCase['Activity'].tolist()):
            declineReasons.append("Lack of Evidence")
        elif "Other Jurisdiction" in justThatCase['Activity'].tolist():
            declineReasons.append("Other Jurisdiction")
        elif "Diversion" in justThatCase['Activity'].tolist():
            declineReasons.append("Diversion")
        else:
            declineReasons.append("Other")

    dispositionReasonDF = pd.DataFrame()
    dispositionReasonDF['File #'] = fnList
    dispositionReasonDF['Disp. Reason'] = declineReasons
    dispositionReasonDF = dispositionReasonDF.groupby('Disp. Reason').size().to_frame().reset_index()
    dispositionReasonDF['source'] = 'B - Declined'
    dispositionReasonDF = dispositionReasonDF.rename(columns={0: 'value'})
    dispositionReasonDF['target'] = "C - " + dispositionReasonDF['Disp. Reason']
    dispositionReasonDF = dispositionReasonDF[['source', 'target', 'value']]
    return dispositionReasonDF