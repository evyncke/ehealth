#!/usr/bin/env python3

#Copyright 2022-4 Eric Vyncke evyncke@cisco.com

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
from urllib import request
import json
import datetime 
import re


# Robert Sparks' suggestion: https://datatracker.ietf.org/api/v1/stats/meetingregistration/?meeting__number=113&limit=2000
# <reg_type>onsite</reg_type> or <reg_type>remote</reg_type>
# <first_name>James</first_name>
# <last_name>Gruessing</last_name>
# <email>james.ietf@gmail.com</email>
# <country_code>NL</country_code>
# <person>/api/v1/person/person/126667/</person>

# object key should probably be person ID

# Currently, lastname, firstname, affiliation, country

def getMeetingParticipants(meetingNumber):
  countriesOnsite = {}
  countriesRemote = {}
  participantsOnsite = {}
  participantsRemote = {}

# Read all participants

# Can be filtered with reg_type=onsite ou remote
  # nextUri= "/api/v1/stats/meetingregistration/?meeting__number={}&limit=200&offset=0&format=xml".format(meetingNumber) + "&reg_type=onsite"
  nextUri= "/api/v1/meeting/registration/?meeting__number={}&limit=200&offset=0&format=xml".format(meetingNumber)

  while (nextUri):
      url = "https://datatracker.ietf.org" + nextUri
      print("Getting", url)
      tree = etree.parse(request.urlopen(url))
      root = tree.getroot()
      meta = root.find('meta')
      nextUri = meta.find('next').text
      totalCount = meta.find('total_count').text
      print("Got {} entries".format(totalCount))
      objects = root.find('objects')
      for object in objects:
        firstName = object.find('first_name').text
        lastName = object.find('last_name').text
        email = object.find('email').text
        person = object.find('person').text
        countryCode = object.find('country_code').text
        if not person:
            continue
        id = int(re.search(r"api/v1/person/person/(.+)/$", person).group(1))
        participant = { 'first_name': firstName, 'last_name': lastName, 'country_code': countryCode, 'email' : email, 'id': id}
        tickets = object.find('tickets')
        registrationType = None
        for ticket in tickets:     
            attendanceType = ticket.find('attendance_type').text
            if attendanceType.endswith('/onsite/'):
                registrationType = 'onsite'
                participantsOnsite[id] = participant
                if countryCode in countriesOnsite:
                    countriesOnsite[countryCode] = countriesOnsite[countryCode] + 1
                else:
                    countriesOnsite[countryCode] = 1
                break
            elif attendanceType.endswith('/remote/'):
                registrationType = 'remote'
                participantsRemote[id] = participant
                if countryCode in countriesRemote:
                    countriesRemote[countryCode] = countriesRemote[countryCode] + 1
                else:
                    countriesRemote[countryCode] = 1
                break

  with open('data/participants_' + str(meetingNumber) + '.js', 'w', encoding = 'utf-8') as f:
      f.write("var participantsOnsite = ")
      json.dump(participantsOnsite, f, ensure_ascii = False, indent = 2)
      f.write(";\n")
      f.write("var countries = ")
      json.dump(countriesOnsite, f, ensure_ascii = False, indent = 2)
      f.write(";\n")
      f.write("var participantsRemote = ")
      json.dump(participantsRemote, f, ensure_ascii = False, indent = 2)
      f.write(";\n")
      now = datetime.datetime.now(datetime.timezone.utc)
      f.write("var registrationCollectionDate = '{}';\n".format(now.isoformat(timespec='seconds')))

  with open('data/remote_' + str(meetingNumber) + '.json', 'w', encoding = 'utf-8') as f:
          json.dump(participantsRemote, f, ensure_ascii = False, indent = 2)

  with open('data/onsite_' + str(meetingNumber) + '.json', 'w', encoding = 'utf-8') as f:
          json.dump(participantsOnsite, f, ensure_ascii = False, indent = 2)

# Load the information about next/current and last meetings
meetings = json.load(open('meetings.json'))

for i in range(123, 126):
  getMeetingParticipants(i)
