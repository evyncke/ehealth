#!/usr/bin/env python3

#Copyright 2022-2025 Eric Vyncke evyncke@cisco.com

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

def getPerson(uri, email = None, role = None):
    # uri looks like api/v1/person/person/111656/
    id = int(re.search(r"api/v1/person/person/(.+)/$", uri).group(1))
    if id in cachedPersons:
        print("Reusing cache for persons")
        if email:
            cachedPersons[id]['email'] = email
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
        personDict['role'] = role
    cachedPersons[int(personId.text)] = personDict
    return personDict

def getGroupFromName(name):
    if not name in cachedGroups:
        print("Unknown name: {}, fetching it".format(name))
        url = "https://datatracker.ietf.org/api/v1/group/group/?format=xml&acronym=" + name 

        tree = etree.parse(request.urlopen(url))
        root = tree.getroot()
        objects = root.find('objects')
        for object in objects:
            state = object.find('state') 
            if not state.text == '/api/v1/name/groupstatename/active/':
                continue
            acronym = object.find('acronym') 
            cachedGroups[acronym.text] = { 'id': object.find('id').text, 'name': object.find('name').text}
            print("Added {} as id={}".format(acronym.text, object.find('id').text))
    return cachedGroups[name]


def getMembers(groupName, roleName):
    print("Looking for {} in {}".format(roleName, groupName))
    group = getGroupFromName(groupName)
    roleSlug = "/api/v1/name/rolename/{}/".format(roleName)
    groupUri = "https://datatracker.ietf.org/api/v1/group/role/?format=xml&group={}&role={}".format(group['id'], roleSlug)
    groupTree = etree.parse(request.urlopen(groupUri))
    groupRoot = groupTree.getroot()
    for object in groupRoot.find('objects'):
        if object.find('name').text != roleSlug:
            continue
        # person email  <email>/api/v1/person/email/Zaheduzzaman.Sarker@ericsson.com/</email>\n  <group>/api/v1/group/group/2/</group>\n  <id type="integer">12152</id>\n  <name>/api/v1/name/rolename/ad/</name>\n  <person>/api/v1/person/person/109753/</person>\n 
        email = re.search(r"api/v1/person/email/(.+)/$", object.find('email').text).group(1)
        getPerson(object.find('person').text, email = email, role = groupName + '-' + roleName)


# Read all groups
if False:
  url = "https://datatracker.ietf.org/api/v1/group/group/?format=xml&limit=1000&offset=0"

  tree = etree.parse(request.urlopen(url))
  root = tree.getroot()
  objects = root.find('objects')
  for object in objects:
      state = object.find('state') 
      if not state.text == '/api/v1/name/groupstatename/active/':
          continue
      acronym = object.find('acronym') 
      cachedGroups[acronym.text] = { 'id': object.find('id').text, 'name': object.find('name').text}

# Or smarter with a per group search ?
# https://datatracker.ietf.org/api/v1/group/group/?acronym=iesg

# Find all IESG members
getMembers('ietf', 'chair')
getMembers('iesg', 'ad')
getMembers('iab', 'chair')
getMembers('iab', 'member')
#getMembers('irtf', 'chair')
#getMembers('irsg', 'member')

with open('leaders.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)

with open('leaders.js', 'w', encoding = 'utf-8') as f:
    f.write("var leaders = ")
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)
    f.write(";\n")
