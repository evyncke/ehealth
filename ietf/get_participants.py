#!/usr/bin/env python3

#Copyright 2022 Eric Vyncke evyncke@cisco.com

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from lxml import etree, html
from urllib import request, error
import json
import datetime 
import sys

# Load the information about next/current and last meetings
meetings = json.load(open('meetings.json'))
meetingNumber = meetings['next']['number']

url = "https://registration.ietf.org/" + str(meetingNumber) + "/participants/?regtype=onsite"

countries = {}
participantsOnsite = {}
participantsRemote = {}

try:
    root = html.parse(request.urlopen(url))
    rows = root.iter('tr')
    # Rows cells are: lastname, firstname, affiliation, country, reg type
    next(rows) # Skip the header
except error.HTTPError:
    # Usually because the meeting registration is not yet open
    rows = []

for row in rows:
        participant = { 'first_name': row[1].text, 'last_name': row[0].text, 'affiliation': row[2].text, 'country_code': row[3].text, 'email' : None, 'id': None}
        participantsOnsite[row[0].text + row[1].text] = participant
        country = row[3].text
        if country in countries:
            countries[country] = countries[country] + 1
        else:
            countries[country] = 1

# Look for remote participants
url = "https://registration.ietf.org/" + str(meetingNumber) + "/participants/?regtype=remote"

try:
    root = html.parse(request.urlopen(url))
    rows = root.iter('tr')
    next(rows) # Skip the header
except error.HTTPError:
    rows = []

for row in rows:
        participant = { 'first_name': row[1].text, 'last_name': row[0].text, 'affiliation': row[2].text, 'country_code': row[3].text, 'email' : None, 'id': None}
        participantsRemote[row[0].text + row[1].text] = participant

with open('participants.js', 'w', encoding = 'utf-8') as f:
    f.write("var participantsOnsite = ")
    json.dump(participantsOnsite, f, ensure_ascii = False, indent = 2)
    f.write(";\n")
    f.write("var countries = ")
    json.dump(countries, f, ensure_ascii = False, indent = 2)
    f.write(";\n")
    f.write("var participantsRemote = ")
    json.dump(participantsRemote, f, ensure_ascii = False, indent = 2)
    f.write(";\n")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("var registrationCollectionDate = '{}';\n".format(now.isoformat(timespec='seconds')))

with open('remote.json', 'w', encoding = 'utf-8') as f:
        json.dump(participantsRemote, f, ensure_ascii = False, indent = 2)

with open('onsite.json', 'w', encoding = 'utf-8') as f:
        json.dump(participantsOnsite, f, ensure_ascii = False, indent = 2)