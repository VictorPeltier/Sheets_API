from staffomatic_api import *
import csv
import pandas as pd
from datetime import datetime, timedelta
import os
from shutil import copy
from sys import exit


def extract_shifts():
	#Checks the day of the extract and extracts the week
	today = datetime.now().date()
	curr_week = today.strftime('%W')
	start_week = today - timedelta(days=today.weekday())
	end_week = start_week + timedelta(days=6)
	end_for_extract = end_week + timedelta(days = 1)
	start_for_extract = start_week - timedelta(days = 7)

	#Creates the starting date of the extract with the tarting date of the week end the end date as well
	date_start = start_for_extract.strftime('%Y-%m-%d')
	date_end = end_for_extract.strftime('%Y-%m-%d')


	#Opens a csv file in which the information will be copied and enters the header
	csv_shift = open('shifts_list.csv','wb')
	writer_shift = csv.writer(csv_shift)
	writer_shift.writerow(['transport_type','zipcode','starts_at','ends_at','shift_length','week','weekday','date','time_start','desired_coverage','nb_subscribers','filling_rate','hours_published','hours_subscribed'])


	#Reads the csv file with the staffomatic assumptions
	assumptions = pd.read_csv('staffomatic_assumptions.csv')

	#Gets all the shifts from the various locations for the appointed period
	bikes, http_status = getShiftsLocationspecific('16381',date_start,date_end)
	print('Bikes shifts extracted')
	cars, http_status = getShiftsLocationspecific('16382',date_start,date_end)
	print('Cars shifts extracted')
	cargoXL, http_status = getShiftsLocationspecific('16384',date_start,date_end)
	print('CargoXL shifts extracted')
	bullitt, http_status = getShiftsLocationspecific('20656',date_start,date_end)
	print('Bullitt shifts extracted')


	#Consolidates all the shifts together
	shifts = bikes  + cars + cargoXL + bullitt


	#Builds the shift information, each line representing a shift, its characteristics, how many people were reqested and how many subscribed
	for shift in shifts:

		#Converts all the Staffomatic ids into logic informations for : a) transport type<>location_id AND b) zipcode <> department_id
		transport_conversion = assumptions.loc[assumptions.loc[:,'Location ID']==shift['location_id'],'transport_type']
		zipcode_conversion = assumptions.loc[assumptions.loc[:,'ID']==shift['department_id'],'Department_zipcode']
		transport = transport_conversion[min(transport_conversion.index.tolist())]
		try:
			zipcode = zipcode_conversion[min(zipcode_conversion.index.tolist())]
		except:
			zipcode = 'Veuillez entrer le zipcode dans le staffomatic asssumptions file'


		#Extracts the relevant data and format it as expected
		start = datetime.strptime(shift['starts_at'],'%Y-%m-%dT%H:%M:%S+01:00')
		end = datetime.strptime(shift['ends_at'],'%Y-%m-%dT%H:%M:%S+01:00')
		date_start = start.strftime('%Y/%m/%d')
		time_start = start.strftime('%H:%M:%S')
		nb_subscribers = len(shift['assigned_user_ids'])
		desired_coverage = shift['desired_coverage']
		week = start.strftime('%W')
		shift_length = ( end - start ).total_seconds() / 3600
		hours_published = desired_coverage * shift_length
		hours_subscribed = nb_subscribers * shift_length
		weekday = start.weekday()


		#Computes the filling rate, leaves a blank if no desired coverage was applied
		try:
			filling_rate = float(nb_subscribers) / float(desired_coverage)
		except:
			filling_rate = ''


		#Writes the data into the csv file
		writer_shift.writerow([
			transport,
			zipcode,
			shift['starts_at'],
			shift['ends_at'],
			shift_length,
			week,
			weekday,
			date_start,
			time_start,
			desired_coverage,
			nb_subscribers,
			filling_rate,
			hours_published,
			hours_subscribed
			])
	csv_shift.close()

if __name__ == '__main__':
	extract_shifts()
