#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

This scripts aims at exracting data on shifts from Staffomatic, search
the target Google spreadsheet in which to compute the results and loads the
data in the 'Raw data' sheet.

It relies on 2 important script :
    a) sheets_API which is a module contining functions to use GSheet API
    b) extract_filling_rate which is a module / script that extracts the past
    2 weeks of shifts from Staffomatic

The different steps to upload the results are the following:
    Step 1: load all the module
    Step 2: extract the shifts - this section is the one that takes the most
    time given low reaction from Staffomatic API
    Step 3: research the Gsheet called 'Paris_filling_rate' and extracts the iD
    Step 4: clear the existing data in the GSheet in the worksheet 'Raw data' and push the data from Staffomatic
    Step 5: format the filling rate as a percentage
    #Step 1
'''

import sheets_API
import extract_filling_rate
import csv


#Step 2
extract_filling_rate.extract_shifts()
print('Les shifts ont été extraits de Staffomatic')

with open('shifts_list.csv','rb') as csvfile:
    reader = csv.reader(csvfile,delimiter = ',')
    shifts_data = [row for row in reader]


#Step 3
spreadsheet_id = sheets_API.search_spreadsheet('Paris_filling_rate')
print('La feuille ayant pour nom "Paris_filling_rate" a l ID {0}'.format(spreadsheet_id))


#Step 4
raw_data_sheet_name = 'Raw data'
noms, tableau = sheets_API.extract_sheets_list(spreadsheet_id)
raw_data_sheet_id = int(tableau.loc[tableau.loc[:,'TITLE']==raw_data_sheet_name,'ID'])
sheets_API.clear_sheet(raw_data_sheet_id, spreadsheet_id)
print('Data in Raw Data sheet has been cleared')
upload = sheets_API.write_data(shifts_data,spreadsheet_id,raw_data_sheet_name)
print('Data has been uploaded into Raw Data')


#Step 5

formatting = 'PERCENT'
pattern = '0%'

sheets_API.change_format(11,12,raw_data_sheet_id, spreadsheet_id, formatting, pattern)
print('Data has been formatted')
