import pandas as pd
import json
import sys
import re

class Venue:
	def __init__(self, nam, ins, reg, cnt, box):
		self.name= nam
		self.instance = ins
		self.region = reg
		self.ric_count = cnt
		self.box_name = box

def dumpVenueToJson(venueObj):
	venueDict = venueObj.__dict__ 
		
	with open('data.txt', 'a') as outfile:  
		json.dump(venueDict, outfile)
		outfile.write('\n')

dictVenueColName = {'AMER': 'AMER Venues', 'EMEA': 'EMEA Venues', 'ASIA': 'Asia Venues'}
dictboxColName = {'AMER': 'TMDPoP CVA Machine', 'EMEA': 'TM DPoP CVA Machine', 'ASIA': 'New DPoP CVA Machine'}
		
		
def extractVenueInfo(region, name, df):

	
	venueRow = df.loc[df[dictVenueColName[region]].str.lower() == name.lower()]
	
	if venueRow.empty:
		print("Venue not found in allocation excel file, name: ", name, ", region: ", region)
		return
	
	inst = venueRow['VAE Instances'].to_string(index=False)
	boxRaw = venueRow[dictboxColName[region]].to_string(index=False)
	cnt = venueRow['Underlying RICs'].to_string(index=False)
	
	# Failed to split with '\n', has to use '\\n'
	boxes = boxRaw.split('\\n')
	boxstr = ""
	
	for box in boxes:
		boxstr += box[0:3]
		boxstr += '/'
	# Remove last ending /
	boxstr = boxstr[:-1]
	boxstr += '-'
	
	boxSearch = re.match(r".*(CVA\d{2}).*", boxRaw)
	
	boxstr += boxSearch.group(1)
	
	
	
	inst = inst[-1]
	
	thisVenue = Venue(name, inst, region, cnt, boxstr.lower())
	dumpVenueToJson(thisVenue)

# Read an excel file and convert into a pandas DataFrame dfVenues
dfOldVenues = pd.read_excel('./CVA_Venues_on_CDMR1.0.xlsx')

# Read a specified sheet in an excel file and convert into a pandas DataFrame dfEMEA
dfEMEA = pd.read_excel('./CVA Production allocation v1.0.84.xls', sheetname="EMEA")
dfAMER = pd.read_excel('./CVA Production allocation v1.0.84.xls', sheetname="AMER")
dfASIA = pd.read_excel('./CVA Production allocation v1.0.84.xls', sheetname="ASIA")

#dfAllocations = dfAllocations.fillna(method='ffill', axis=1)

# As merged cells are used in excel CVA Production allocation
# So there are some merged columns such as 'TM DPoP CVA Machine' own values as NaN (blank values) in some rows.
# Funciton ffill is to forward fill all NaN with previous valid values.
# ffill cannot change the DataFrame itslef, the changes of ffill will be applied to the return new DataFrame

dfEMEAfilled = dfEMEA.ffill()
dfAMERfilled = dfAMER.ffill()
dfASIAfilled = dfASIA.ffill()

#venueline = dfAllocations.loc[dfAllocations['EMEA Venues'] == "Equiduct"]

#firstline = newdf.loc[2]

#data['venues'].append({'A':'valueA', 'B': 'valueB'})

with open('data.txt', 'w'): pass

# Iterate all rows in DataFrame dfOldVenues
for index, row in dfOldVenues.iterrows():
	# For each venue row, find its region firstly, then look up it in the right sheet DataFrame
	if row['Reigon'] == "AMER":
		venueObj = extractVenueInfo(row['Reigon'], row['Name'], dfAMERfilled)
	elif row['Reigon'] == "EMEA":
		venueObj = extractVenueInfo(row['Reigon'], row['Name'], dfEMEAfilled)
	elif row['Reigon'] == "ASIA":
		venueObj = extractVenueInfo(row['Reigon'], row['Name'], dfASIAfilled)

		#venueline = dfAMERfilled.loc[dfAMERfilled['AMER Venues'] == row['Name']]

	#print(venueline['TM DPoP CVA Machine'], venueline['TM DPoP CVA Machine'])