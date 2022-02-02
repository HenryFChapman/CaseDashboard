import pandas as pd 
from KarpelStarter import karpelStarter
import plotly.graph_objects as go
import numpy as np
from DispositionCounter import disposedCaseCounter, declinedCaseCounter

def factorize(s):
    a = pd.factorize(s, sort=True)[0]
    return (a + 0.01) / (max(a) + 0.1)


def reasonsToNodes(reasonDF, links):

	reasonDictionaries = reasonDF.to_dict(orient = 'records')
	#print(reasonDictionaries)

	links.extend(reasonDictionaries)

	return links

def generateJCPOCaseHistory(year, crimeCategory, receivedFileNumbers, listOfKarpelCases):

	#Received - Count Unique File Numbers - Number of Received Cases
	#print("Received Cases: " + str(len(receivedFileNumbers)))

	#Filed - Count How Many of Those File Numbers Appear in Filed
	filedSet = set(listOfKarpelCases[1]['File #'].tolist())
	filedFileNumbers = filedSet.intersection(receivedFileNumbers)

	#Not Filed - Count How Many of Those File Numbers Appear in Not-Filed
	declinedSet = set(listOfKarpelCases[3]['File #'].tolist())
	declinedFileNumbers = declinedSet.intersection(receivedFileNumbers)
	declinedFileNumbers = declinedFileNumbers.difference(filedSet)
	declineReasons = declinedCaseCounter(declinedFileNumbers, listOfKarpelCases[3])

	#Under Review = Received - Filed - Not Filed
	reviewSet = set(receivedFileNumbers).difference(filedSet).difference(declinedFileNumbers)

	#Disposed Cases
	disposedSet = set(listOfKarpelCases[2]['File #'].tolist())
	disposedFileNumbers = disposedSet.intersection(receivedFileNumbers)
	disposedFileNumbers = list(disposedSet.intersection(filedFileNumbers))
	disposalReasons = disposedCaseCounter(disposedFileNumbers, listOfKarpelCases[2])
	#print(disposalReasons.head())

	#Currently Pending/Under Warrant Status
	#Currently Pending = Filed - Disposed
	activeSet = set(filedFileNumbers).difference(disposedFileNumbers)

	#Review Position
	reviewPos = len(reviewSet)/len(receivedFileNumbers)
	declinePos = reviewPos - len(declinedFileNumbers)/len(receivedFileNumbers)
	filedPos = declinePos - len(filedFileNumbers)/len(receivedFileNumbers)
	activePos = filedPos - len(activeSet)/len(receivedFileNumbers)
	disposedPos = len(declinedFileNumbers)/len(receivedFileNumbers)

	links = [
		{'source': 'A - Received by Office', 'target':'B - Declined', 'value':len(declinedFileNumbers)},
		{'source': 'A - Received by Office', 'target':'B - Under Review', 'value':len(reviewSet)},
		{'source': 'A - Received by Office', 'target':'B - Cases Filed', 'value':len(filedFileNumbers)},
		{'source': 'B - Cases Filed', 'target':'C - Case Active', 'value':len(activeSet)},
		{'source': 'B - Cases Filed', 'target':'C - Cases Disposed', 'value':len(disposedFileNumbers)},
	]

	reasonsToNodes(disposalReasons, links)
	reasonsToNodes(declineReasons, links)

	df = pd.DataFrame(links)

	nodes = np.unique(df[["source","target"]], axis=None)
	nodes = pd.Series(index=nodes, data=range(len(nodes)))

	#work out node position
	nodes = (
		nodes.to_frame("id").assign(
			x = lambda d: factorize(d.index.str[0]),
			y = lambda d: factorize(d.index.str[0])/3,
		)
	)

	fig = go.Figure(
    	go.Sankey(
    		arrangement = "snap",
    	    node={"label": nodes.index.str[3:], "x": nodes["x"], "y": nodes["y"]},
    	    link={
    	        "source": nodes.loc[df["source"], "id"],
    	        "target": nodes.loc[df["target"], "id"],
     	       	"value": df["value"],
     	       	"color": 'grey'
     	   },
    	)
	)

	fig.update_layout(title =  dict(text ="Current Progress of " + crimeCategory + " Cases Received in " + str(year),
                               font =dict(size=30,
                               color = 'Black')), font_size=10, title_x=0.5)


	#fig.update_layout(title =  dict(text ="Current Progress of " + crimeCategory + " Cases Received in " + str(year),
    #                           font =dict(size=30,
    #                           color = 'White')), font_size=15, title_x=0.5, plot_bgcolor='rgba(34,34,34,255)', paper_bgcolor='rgba(34,34,34,255)',)

	path = "C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\KCPD Clearance Dashboard\\Sankeys\\KarpelDashboard\\"
	fig.write_html(path + str(year) + " - " +crimeCategory + ".html")

