import pycurl
import json
import cStringIO
from urllib import urlencode

with open('auth/credentials.txt','rb') as file:
	credentials = file.read()

with open('auth/domain_name.txt','rb') as file:
    domain_name = file.read()

def getFromServer(url):
	"""

	Make a GET request to the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	# Setup a string buffer to store the server response
	buf = cStringIO.StringIO()

	# Create the curl request with all the parameters and execute it
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.USERPWD, '{credz}'.format(credz = credentials))
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	# Retrieve the actual data
	server_response = json.loads(buf.getvalue())
	http_status = c.getinfo(c.HTTP_CODE)
	buf.close()
	return server_response, http_status

def postToServer(url, data):
	"""

	Make a POST request to the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	# Setup a string buffer to store the server response
	buf = cStringIO.StringIO()

	# Encode the data for url standards
	data_encoded = urlencode(data)

	# Create the curl request with all the parameters and execute it
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.USERPWD, '{credz}'.format(credz = credentials))
	c.setopt(c.POSTFIELDS, data_encoded)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	# Retrieve the actual data
	server_response = json.loads(buf.getvalue())
	http_status = c.getinfo(c.HTTP_CODE)
	buf.close()
	return server_response, http_status


def getLocations():
	"""

	Retrieve all the locations using the staffomatic API.
	Returns the locations and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/locations.json'.format(domain = domain_name)
	locations, http_status = getFromServer(url)
	return locations, http_status


def getDepartments(location_id):
	"""
	Retrieve all the departments for a specified location using the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/locations/{location}/departments.json'.format(domain = domain_name, location = location_id)
	departments, http_status = getFromServer(url)
	return departments, http_status


def getSchedules(location_id):
	"""
	Retrieve all the schedules for a specified location using the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/locations/{location}/schedules.json'.format(domain = domain_name, location = location_id)
	schedules, http_status = getFromServer(url)
	return schedules, http_status

def createShift(location_id, department_id, schedule_id, from_timestamp, to_timestamp, coverage, open_end):
	"""
	Create a shift using the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	# Format the data that will be sent through the CURL request
	shift_data = {
		'starts_at' : '%s' % from_timestamp,
		'ends_at' : '%s' % to_timestamp,
		'open_end' : '%s' % open_end,
		'department_id' : '%s' % department_id,
		'location_id' : '%s' % location_id,
		'desired_coverage': '%s' % coverage,
		'note' : ''
	}

	# Create the shift
	url = 'https://api.staffomaticapp.com/v3/{domain}//schedules/{schedule}/shifts.json'.format(domain = domain_name, schedule = schedule_id)
	shift, http_status = postToServer(url, shift_data)
	return shift, http_status

def getUsers(location_id):
	"""
	Retrieve all the users from a specific location using the staffomatic API.
	Returns the locations and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/locations/{location}/users.json'.format(domain = domain_name, location = location_id)
	users, http_status = getFromServer(url)
	return users, http_status


def putToServer(url, data):
	"""
	Make a PUT request to the staffomatic API.
	Returns the server response and the HTTP status.
	"""

	# Setup a string buffer to store the server response
	buf = cStringIO.StringIO()

	# Encode the data for url standards
	data_encoded = urlencode(data)

	# Create the curl request with all the parameters and execute it
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.USERPWD, '{credz}'.format(credz = credentials))
	c.setopt(pycurl.CUSTOMREQUEST, 'PUT')
	c.setopt(c.POSTFIELDS, data_encoded)
	c.setopt(c.WRITEFUNCTION, buf.write)
	#c.setopt(c.VERBOSE, True)
	c.perform()

	# Retrieve the actual data
	server_response = json.loads(buf.getvalue())
	http_status = c.getinfo(c.HTTP_CODE)
	buf.close()
	return server_response, http_status


def changeId(location_id,user_id,custom_id):
	"""
	Change the customiD of a driver based on his Staffomatic iD
	"""

	# Format the data that will be sent through the CURL request
	user_data = {
		'custom_id': 'id %s' % (custom_id)
		}


	url = 'https://api.staffomaticapp.com/v3/{domain}/locations/{location}/users/{user}.json'.format(domain = domain_name, location = location_id, user = user_id)
	user, http_status = putToServer(url,user_data)
	return user, http_status


def getShifts(start,end):
	"""
	Retrieve all the shifts from a department using the staffomatic API.
	Returns the shift and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/shifts.json?from={start_t}T00:00:00+02:00&until={end_t}T00:00:00+02:00'.format(domain = domain_name, start_t = start, end_t = end)
	shifts, http_status = getFromServer(url)
	return shifts, http_status


def getShiftsLocationspecific(location,start,end):
	"""
	Retrieve all the shifts from a location using the staffomatic API.
	Returns the shift and the HTTP status.
	"""

	url = 'https://api.staffomaticapp.com/v3/{domain}/locations/{location}/shifts.json?from={start_t}T00:00:00+02:00&until={end_t}T00:00:00+02:00'.format(domain = domain_name, location = location, start_t = start, end_t = end)
	shifts, http_status = getFromServer(url)
	return shifts, http_status


def inviteUser(email, location_id, custom_id):
	"""
	Create a user using the staffomatic API.
	Returns the server response and the HTTP status.
	"""
	# Format the data that will be sent through the CURL request

	user_data = {
		'email' : '%s' % email,
		'department_ids' : [76365, 71154, 72581, 66852, 66841, 66997, 66995, 69411, 68934, 66996, 66998],
		'do' : 'send_invitation',
		'custom_id' : 'id %s' % custom_id
		}
	# Create the user
	url = 'https://api.staffomaticapp.com/v3/{domain}//locations/{location}/users.json'.format(domain = domain_name, location = location_id)
	user, http_status = postToServer(url, user_data)
	return user, http_status
