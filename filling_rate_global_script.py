#!/usr/bin/python
# -*- coding: utf-8 -*-


from sheets_API import *
import extract_filling_rate

extract_filling_rate.extract_shifts()
print('Les shifts ont été extraits de Staffomatic')

with open('shifts_list.csv','rb') as csvfile:
    reader = csv.reader(csvfile,delimiter = ',')
    shifts_data = [row for row in reader]

spreadsheet_id = search_spreadsheet('Paris_filling_rate')
print('La feuille ayant pour nom "Paris_filling_rate" a l ID {0}'.format(spreadsheet_id))

raw_data_sheet_name = 'Raw data'

upload = write_data(shifts_data,spreadsheet_id,raw_data_sheet_name)
print('Les données ont été uploadées dans Raw Data')

noms, tableau = extract_sheets_list(spreadsheet_id)

raw_data_sheet_id = int(tableau.loc[tableau.loc[:,'TITLE']==raw_data_sheet_name,'ID'])

formatting = 'PERCENT'
pattern = '0%'

change_format(11,12,raw_data_sheet_id, spreadsheet_id, formatting, pattern)
print('Les données ont été formattées')
