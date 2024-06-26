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

url = "https://registration.ietf.org/" + str(meetingNumber) + "/participants/onsite/"

countries = {}
participants = []

try:
    root = html.parse(request.urlopen(url))
    rows = root.iter('tr')
    next(rows) # Skip the header
except error.HTTPError:
    # Usually because the meeting registration is not yet open
    rows = []

fjs = open('participants.js', 'w', encoding = 'utf-8')
fjs.write("var participantsOnsite = [")
for row in rows:
        fjs.write('["{}", "{}", "{}", "{}"],'.format(row[0].text, row[1].text, row[2].text, row[3].text))
        participants.append([row[0].text, row[1].text, row[2].text, row[3].text])
        country = row[3].text
        if country in countries:
            countries[country] = countries[country] + 1
        else:
            countries[country] = 1
fjs.write("] ;\n")

fjs.write("var countries = ")
json.dump(countries, fjs, ensure_ascii = False, indent = 2)
fjs.write(";\n")

with open('onsite.json', 'w', encoding = 'utf-8') as f:
        json.dump(participants, f, ensure_ascii = False, indent = 2)

# Look for remote participants
url = "https://registration.ietf.org/" + str(meetingNumber) + "/participants/remote/"

participants = []
try:
    root = html.parse(request.urlopen(url))
    rows = root.iter('tr')
    next(rows) # Skip the header
except error.HTTPError:
    rows = []

fjs.write("var participantsRemote = [")
for row in rows:
        fjs.write('["{}", "{}", "{}", "{}"],\n'.format(row[0].text, row[1].text, row[2].text, row[3].text))
        participants.append([row[0].text, row[1].text, row[2].text, row[3].text])
fjs.write("] ;\n")

with open('remote.json', 'w', encoding = 'utf-8') as f:
        json.dump(participants, f, ensure_ascii = False, indent = 2)

now = datetime.datetime.now(datetime.timezone.utc)
fjs.write("var registrationCollectionDate = '{}';\n".format(now.isoformat(timespec='seconds')))

fjs.close()
