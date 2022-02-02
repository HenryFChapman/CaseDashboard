# Jackson County Prosecutor Cases Dashboard
![alt text](https://github.com/HenryFChapman/ProsecutorCasesDashboard/blob/main/DashboardScreenshot.png)
In a move to promote law enforcement transparency, the Jackson County Prosecutor's Office has published a [dashboard](www.tinyurl.com/ProsecutorCases/), which shows up-to-date statistics on how the office processes criminal cases. 

This is the backend code that powers the Jackson County Prosecutor's Office Dashboard. It's written in Python using Pandas, GeoPandas, numpy, shapely, and a few other libraries. It uses LocationIQ for its geocoding, but we plan to upgrade that to a more robust geocoder soon. 

## How the Dashboard Works
![alt text](https://github.com/HenryFChapman/ProsecutorCasesDashboard/blob/main/Case%20Process%20Flowchart.png)
### Data Query
Every day at 6:00 PM, we run an internal query that exports every received, not-filed, filed, and disposed charge of that year to their respective CSV file. We pull 20 different features for each charge including the defendant's name, date of birth, police incident number, internal file number, and many others. 

### Data Analysis
The code published here handles the data analysis portion of the dashboard. 

#### karpelDashboardRunner.py
This is the main script that calls each of the other functions.

#### KarpelStarter.py
This script fetches the daily queried data. It lightly cleans the data (i.e. dropping known "test" defendants), filters it by the current year, and exports each case type (received, not-filed, filed, and disposed) to a unique CSV.

#### DefendantDemographics.py
This script handles the analysis for examining defendant demographics (age, race, and sex). It does this by case category (homicides, assaults, etc).

#### CaseDetails.py
This script handles the analysis for examining case information like disposal timelines, declination reasons, and trial outcomes.

#### Methodology for Calculating Trial Results
Calculating how many trials occured is a complicated process. 
* I isolate Disposed Cases with a trial verdict. Trial verdicts include Guilty or Not Guilty verdicts. If a case has at least 1 trial verdict a trial occured.
* To determine guilt, if at least 1 guilty verdict appears, that is a guilty case. Otherwise, it's a not guilty case.
Limitations:
* Doesn't include mistrials.
* Doesn't include cases on the verge of trial/incomplete trials.
* Calculations by Category
* Using Disposal Dates
* Trials Across Years/Split Verdicts

#### DashboardMapGenerator.py
This script handles the hex map creation. It first ensures that all points are geocoded. Next, it counts points per uniform hex using a spatial join. Lastly, it concatenates all those categories, then exports them to a geojson file. 

### Data Publishing
Once all the analysis has been completed, the program concatenates the large csv file and imports it to our dashboard's front-end, an ESRI Operations Dashboard.

## Data Definitions

### Referred Case
The first move through our office is a case referral, or when a police agency submits a Probable Cause Statement (PC). A PC is an affirmation from a law enforcement officer that a criminal act has occured. Once our office receives a PC, legal assistants enter the case into Karpel, our records management system. Any time a case is received, every underling charge ends up in the set of all Received Cases.

### Not-Filed Case
Upon receiving the case, our office can decline to file any of its underlying charges. Cases are declined for many reasons. For example, the suspect or victim may be deceased. The statute of limitations might be expired. The most common decline reason is that of insufficient evidence. When charges are declined, the attorney or legal assistant update the status in Karpel. All declined charges end up in the set of all Not-Filed Cases.

### Filed Case
If our office makes the determination that the crime occured beyond a reasonable doubt, our office decides to file charges in the case. The charges actually filed can differ significatly from the charges the police officer thought might be appropriate. When any of the underlying charges of a case are filed, the overall case ends up in the set of Filed Cases.

### Disposed Case
Disposed cases are filed cases that have completed their journey through the Jackson County Courthouse. They conclude usually with a guilty plea, but can have many disposition reasons. For example, our office might dismiss the case due to an evidentiary issue. Every underlying charge within a case are disposed at one time, usually after the sentencing phase. 