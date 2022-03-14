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

cachedPersons = {}
cachedGroups = {}
groupsMeeting = {}

def getPerson(uri, email = None, role = None):
    global  cachedPersons

    # uri looks like api/v1/person/person/111656/
    id = int(re.search(r"api/v1/person/person/(.+)/$", uri).group(1))
    if id in cachedPersons:
        print("Reusing cache")
        if email:
            cachedPersons[id]['email'] = email
        if role:
            cachedPersons[id]['role'].append(role)
        return cachedPersons[id]
    url =  "https://datatracker.ietf.org" + uri + '?format=xml'
    personTree = etree.parse(request.urlopen(url))
    personRoot = personTree.getroot()
    ascii = personRoot.find('ascii')
    name = personRoot.find('name')
    personId = personRoot.find('id')
    personDict = {'ascii': ascii.text, 'name': name.text}
    if email:
        personDict['email'] = email
    if role:
        personDict['role'] = [role]
    cachedPersons[int(personId.text)] = personDict
    return personDict

def getGroupFromName(name):
    global cachedGroups
    if not name in cachedGroups:
        print("Unknown name: {}".format(name))
    return cachedGroups[name]


def getMembers(groupName, roleName):
    print("Looking for {} in {}".format(roleName, groupName))
    group = getGroupFromName(groupName)
    roleSlug = "/api/v1/name/rolename/{}/".format(roleName)
    groupUri = "https://datatracker.ietf.org/api/v1/group/role/?format=xml&group={}&name={}".format(group['id'], roleName)
    groupTree = etree.parse(request.urlopen(groupUri))
    groupRoot = groupTree.getroot()
    for object in groupRoot.find('objects'):
        if object.find('name').text != roleSlug:
            continue
        email = re.search(r"api/v1/person/email/(.+)/$", object.find('email').text).group(1)
        getPerson(object.find('person').text, email = email, role = groupName + '-' + roleName)

def getBlueSheets(groupName):
    global cachedGroups
    print("Looking for blue sheets for {}".format(groupName))
    group = getGroupFromName(groupName)
    blueSheetUri = "https://datatracker.ietf.org/api/v1/doc/document/?format=xml&group={}&type=bluesheets&time__gte={}".format(group['id'], lastMeetingDate)
    tree = etree.parse(request.urlopen(blueSheetUri))
    root = tree.getroot()
    # There could be several interimes since that time...
    for object in root.find('objects'):
        name = object.find('name')
        if name is None or '-interim-' in name.text:
            continue
        uploadedFilename = object.find('uploaded_filename')
        if uploadedFilename is None or uploadedFilename.text == '':
            continue
        cachedGroups[groupName]['bluesheets'] = uploadedFilename.text
        return

# Should get the meeting ID from https://datatracker.ietf.org/api/v1/meeting/meeting/?type=ietf&offset=0&limit=1
# Value is in <id type="integer">1532</id>
meetingID = 1532
lastMeetingDate = "2021-11-01T00:00:00"

# TODO should also get the start date to get back the blue sheets

# Read all sessions from the schedule
nextUri= "/api/v1/meeting/session/?meeting=" + str(meetingID) + "&type=regular&format=xml&limit=200&offset=0"
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    print("Getting", url)
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    objects = root.find('objects')
    for object in objects:
        group = object.find('group').text
        meeting = object.find('meeting').text
        onAgenda = object.find('on_agenda')
        if onAgenda is None or onAgenda.text != 'True':
            continue
        purpose = object.find('purpose')
        if purpose is None or purpose.text != '/api/v1/name/sessionpurposename/regular/':
            continue
        requestedDuration = object.find('requested_duration')
        if requestedDuration is None or requestedDuration.text == '0:00:00':
            continue
        if meeting != '/api/v1/meeting/meeting/' + str(meetingID) + '/':
            print("Unexpected meeting:", meeting)
            continue
        groupsMeeting[group] = True

print(groupsMeeting)

# Read all groups
nextUri= "/api/v1/group/group/?format=xml&limit=200&offset=0"
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    print("Getting", url)
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    objects = root.find('objects')
    for object in objects:
        if object.find('id').text == '2318' or object.find('id').text == '2319':
            print(object.find('id').text, object.find('state').text, object.find('type').text)
        state = object.find('state') 
        if state.text != '/api/v1/name/groupstatename/active/' and state.text != '/api/v1/name/groupstatename/bof/':
            continue
        acronym = object.find('acronym') 
        listEmail = object.find('list_email') 
        # Type can be /api/v1/name/grouptypename/rg/ or nomcom or sdo, team, area, or wg
        groupTypeName = object.find('type').text
        groupType = re.search(r'/api/v1/name/grouptypename/(.+)/', groupTypeName).group(1)
        # Only save active WG
        if groupType == 'wg':
            resourceUri = object.find('resource_uri')
            if resourceUri is not None and resourceUri.text in groupsMeeting:
                meeting = True
            else:
                meeting = False
            cachedGroups[acronym.text] = { 'id': object.find('id').text, 'name': object.find('name').text, 'type': groupType, 'meeting': meeting}
            if listEmail.text:
                cachedGroups[acronym.text]['list_email'] = listEmail.text


# Loop for all active WG
for group in cachedGroups:
    getMembers(group, 'chair')
    getMembers(group, 'delegate')
    getBlueSheets(group)

with open('wgchairs.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)

with open('wgchairs.js', 'w', encoding = 'utf-8') as f:
    f.write("var wgChairs = ")
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar wgChairsCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))

with open('wg.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedGroups, f, ensure_ascii = False, indent = 2)

with open('wg.js', 'w', encoding = 'utf-8') as f:
    f.write("var wgs = ")
    json.dump(cachedGroups, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar wgsCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))
