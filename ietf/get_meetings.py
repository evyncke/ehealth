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

from lxml import etree
from urllib import request
import json
import datetime 
import re

meetings = {}

def buildMeetingObject(meetingElem):
    meetingObject = {}
    meetingObject['id'] = int(meetingElem.find('id').text)
    meetingObject['country2'] = meetingElem.find('country').text
    meetingObject['date'] = meetingElem.find('date').text
    meetingObject['number'] = int(meetingElem.find('number').text)
    return meetingObject 

# Read last two meetings
url = "https://datatracker.ietf.org/api/v1/meeting/meeting/?type=ietf&offset=0&limit=2&format=xml"

tree = etree.parse(request.urlopen(url))
root = tree.getroot()
objects = root.find('objects')

meetings['next'] = buildMeetingObject(objects[0])
meetings['last'] = buildMeetingObject(objects[1])

with open('meetings.json', 'w', encoding = 'utf-8') as f:
    json.dump(meetings, f, ensure_ascii = False, indent = 2)

with open('meetings.js', 'w', encoding = 'utf-8') as f:
    f.write("var meetings = ")
    json.dump(meetings, f, ensure_ascii = False, indent = 2)
    f.write(";\n")
