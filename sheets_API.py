from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.file import Storage
import time
import datetime
import csv
import os
import pandas as pd
import numpy as np

def authenticate():
    """ Authenticate through OAuth v2 to Sheets API v4 and
    returns the API endpoint to use under the name SHEETS"""
    #Create the flags
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    path_start = os.getcwd()

    #Set the parameters of Google Authentication
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive'
    CLIENT_SECRET = '%s/auth/client_secret.json' % path_start
    APPLICATION_NAME = 'client_filling'

    #Store the credentials
    store = file.Storage('%s/auth/storage.json' %path_start)
    credz = store.get()
    if not credz or credz.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
        credz = tools.run_flow(flow,store,flags)


    #Initialize the API endpoint to communicate with Google API
    SHEETS = build('sheets','v4',http=credz.authorize(Http()))
    DRIVE = build('drive','v3',http=credz.authorize(Http()))
    return SHEETS, DRIVE

SHEETS = authenticate()[0]
DRIVE = authenticate()[1]

def push(request_data,spreadsheet_id):
    ''' Take all the "request_data", formatted as per Sheets API v4 standards and pass the
    parameters into a batchUpdate of the sheet "spreadsheet_id"'''
    data = []
    data.append(request_data)
    body = {'requests':data}
    result = SHEETS.spreadsheets().batchUpdate(
        spreadsheetId = spreadsheet_id,
        body = body
    ).execute()


def clear_sheet(sheet_id, spreadsheet_id):
    '''Clear the specified sheet of the spreadsheet with spreadsheet_id of all values'''
    requests_to_pass = []

    requests_to_pass.append({
        "updateCells":{
            "range": {
                "sheetId": sheet_id
            },
            "fields":"userEnteredValue"
        }
    })

    body = {
        "requests":requests_to_pass
    }

    batch_update(body, spreadsheet_id)




def write_data(request_data,spreadsheet_id,sheet_name):

    ''' Takes all the data entered as request_data and push the values to the spreadsheet with spreadsheet_id
    in the sheet called sheet_name'''

    range_to_update = '{0}!A1'.format(sheet_name)

    data = [{
        'range':range_to_update,
        'values':request_data,
        'majorDimension':'ROWS'
    }]
    body = {
        'valueInputOption':'USER_ENTERED',
        'data':data,
        'includeValuesInResponse':False
    }
    SHEETS.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body = body,
    ).execute()


def batch_update(body,spreadsheet_id):
    ''' Does a batchUpdate request in Google Sheets API v4 with the entered body'''
    response = SHEETS.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body = body,
    ).execute()
    print(response.get('replies')[0].get('findReplace'))



def change_format(start_column, end_column, sheet_id, spreadsheet_id, type_format, pattern_format):
    '''Change the format of the specified columns of the spreadsheet with spreadsheet_id to format specified'''
    requests_to_pass = []


    requests_to_pass.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startColumnIndex": start_column,
                "endColumnIndex": end_column
            },
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {
                        "type": type_format,
                        "pattern": pattern_format
                    }
                }
            },
            "fields": "userEnteredFormat.numberFormat"
        },
    })

    body = {
        "requests": requests_to_pass
    }

    batch_update(body, spreadsheet_id)




def search_spreadsheet(sheet_name):

    ''' This function searches for a spreadsheet named as the parameter passed and returns
    the first one in the results. It returns spreadsheet_id'''

    params = {'q':"mimeType='application/vnd.google-apps.spreadsheet' and name contains '%s'"%sheet_name}
    data = DRIVE.files().list(**params).execute()
    file_list = data.get('files',[])
    formatted_list = pd.DataFrame.from_dict(file_list)
    try:
        spreadsheet_id = formatted_list.loc[0,'id']
        return spreadsheet_id
    except:
        print('Sorry, no spreadhsheet have been found meeting the name criterion try another name')


def extract_sheets_list(spreadsheet_id):

    '''Extracts the list of sheets within the spreadsheet with given spreadsheet_id'''

    #This section is getting the sheet with the id passed as a parameter
    params_fr_sheet = {'spreadsheetId':spreadsheet_id}
    sheet_metadata = SHEETS.spreadsheets().get(**params_fr_sheet).execute()
    sheets = sheet_metadata.get('sheets')

    #This section is extracting the list of titles of the sheet
    titles = []
    for sheet in sheets:
        titles.append({'ID':sheet.get('properties').get('sheetId'),'TITLE':sheet.get('properties').get('title')})
        export_sheets = pd.DataFrame.from_dict(titles)
        titres = [x for x in export_sheets.loc[:,'TITLE']]
    return titres, export_sheets

def check_name(sheet_name,spreadsheet_id):

    '''Checks if a sheet_name is within the titres of a spreadsheet_id and
    creates a new sheet with the sheet_name as title if it's not the case'''

    titres, export_sheets = extract_sheets_list(spreadsheet_id)

    if '{0}'.format(sheet_name) in titres:
        print "The sheet named '{0}' already exists".format(sheet_name)
    else:
        data = {'properties':{'title':'{0}'.format(sheet_name)}}

        requests = {
            'requests':[{
                "addSheet":data
            }]
        }

        new_file = SHEETS.spreadsheets().batchUpdate(
            spreadsheetId = spreadsheet_id,
            body = requests
        ).execute()

        infos = new_file.get('replies')[0].get('addSheet')
        print('Created a new sheet called {0} with ID: {1}'.format(infos.get('properties').get('title'),infos.get('properties').get('sheetId')))
        return
