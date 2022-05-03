import os
import json
import arcgis
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from arcgis.features import FeatureLayerCollection

# Script: DataUploader.py
# Purpose:  This script uploads the CombinedData.csv, individual polygons, and individual points file to ESRI Online. It uses a native ArcPy 
# 			installation to accomplish this for authentication purposes. 
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: json, ArcGisPro, pandas
#	 Functions: main()
def main():

	homeFolder = r"C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\"

	print("Starting upload")
	gis = GIS("home")

	print("Karpel Dashboard")
	#Upload Combined Data to Karpel Dashboard
	feature_layer_item = gis.content.search("1466e21a965849848e9ad8dd56faf979")[0]
	print(feature_layer_item)
	flayers = feature_layer_item.tables
	flayer = flayers[0]
	flayer.manager.truncate()
	data_file_location = homeFolder + r'Karpel Dashboard - v2.0\CombinedDataV2.csv'
	flayerNew = FeatureLayerCollection.fromitem(feature_layer_item)
	flayerNew.manager.overwrite(data_file_location)

	print("Karpel Dashboard - Polygons")
	#Polygons
	#Uploads hexes to ESRI dashboard 
	feature_layer_item = gis.content.search("47f3dff59fbc451984392d07c1d39f9b")[0]
	print(feature_layer_item)
	flayers = feature_layer_item.layers
	flayer = flayers[0]
	flayer.manager.truncate()
	data_file_location = homeFolder + r'Karpel Dashboard - v2.0\Maps\MasterSpatialDataFixedV2.geojson'
	flayerNew = FeatureLayerCollection.fromitem(feature_layer_item)
	flayerNew.manager.overwrite(data_file_location)

if __name__ == "__main__":
	main()