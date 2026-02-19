#!/usr/bin/env python3

#Copyright 2022-2026 Eric Vyncke evyncke@cisco.com

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
cachedDirectorates = {}
directorateMeeting = {}

# Load the information about next/current and last meetings
meetings = json.load(open('meetings.json'))

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

def getDirectorateFromName(name):
    global cachedDirectorates
    if not name in cachedDirectorates:
        print("Unknown name: {}".format(name))
    return cachedDirectorates[name]

def getMembers(directorateName, roleName):
    print("Looking for {} in {}".format(roleName, directorateName))
    directorate = getDirectorateFromName(directorateName)
    roleSlug = "/api/v1/name/rolename/{}/".format(roleName)
    directorateUri = "https://datatracker.ietf.org/api/v1/group/role/?format=xml&group={}&name={}".format(directorate['id'], roleName)
    print('Fetching', directorateUri)
    directorateTree = etree.parse(request.urlopen(directorateUri))
    directorateRoot = directorateTree.getroot()
    for object in directorateRoot.find('objects'):
        if object.find('name').text != roleSlug:
            continue
        email = re.search(r"api/v1/person/email/(.+)/$", object.find('email').text).group(1)
        getPerson(object.find('person').text, email = email, role = directorateName + '-' + roleName)

meetingID = meetings['next']['id']
lastMeetingDate = meetings['last']['date']

# TODO should also get the start date to get back the blue sheets

# Read all directorates
nextUri= "/api/v1/group/group/?format=xml&limit=200&offset=0&type=review&state=active"
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    print("Getting", url)
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    objects = root.find('objects')
    for object in objects:
        acronym = object.find('acronym') 
        print('Acronym', acronym.text)
        listEmail = object.find('list_email') 
        # Type can be /api/v1/name/grouptypename/rg/ or nomcom or sdo, team, area, or wg
        directorateTypeName = object.find('type').text
        groupType = re.search(r'/api/v1/name/grouptypename/(.+)/', directorateTypeName).group(1)
        # Only save review group
        if groupType == 'review':
            resourceUri = object.find('resource_uri')
            cachedDirectorates[acronym.text] = { 'id': object.find('id').text, 'name': object.find('name').text, 'type': directorateTypeName }
            if listEmail.text:
                cachedDirectorates[acronym.text]['list_email'] = listEmail.text


# Loop for all active WG
for directorate in cachedDirectorates:
    getMembers(directorate, 'chair')
    getMembers(directorate, 'delegate')
    getMembers(directorate, 'secr')
    getMembers(directorate, 'member')
    getMembers(directorate, 'reviewer')


with open('dirmembers.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)

with open('dirmembers.js', 'w', encoding = 'utf-8') as f:
    f.write("var directorateMembers = ")
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar directorateMembersCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))

with open('directorate.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedDirectorates, f, ensure_ascii = False, indent = 2)

with open('directorate.js', 'w', encoding = 'utf-8') as f:
    f.write("var directorates = ")
    json.dump(cachedDirectorates, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar directoratesCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))
