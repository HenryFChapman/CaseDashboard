import subprocess

# Script: DataUploaderRunner.py
# Purpose:  This script actually runs the DataUploader script with ArcPy installation.
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: subprocess
#	 Functions: DataUploaderRunner()

def DataUploaderRunner():

	#Path to Local ArcPy Installation
	pythonPath = r"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
	
	#Path to DataUploader Script
	scriptPath = r"C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Karpel Dashboard - v2.0\DataUploader.py"

	#Call SubProcess
	subprocess.check_call([pythonPath, scriptPath])