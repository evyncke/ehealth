#!/usr/bin/env python3

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
        print("Reusing cache")
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
        print("Unknown name: {}".format(name))
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
        email = re.search(r"api/v1/person/email/(.+)/$", object.find('email').text).group(1)
        getPerson(object.find('person').text, email = email, role = groupName + '-' + roleName)


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
        if not object.tag == 'object':
            print('error')
        state = object.find('state') 
        if not state.text == '/api/v1/name/groupstatename/active/':
            continue
        acronym = object.find('acronym') 
        # Type can be /api/v1/name/grouptypename/rg/ or nomcom or sdo, team, area, or wg
        groupTypeName = object.find('type').text
        groupType = re.search(r'/api/v1/name/grouptypename/(.+)/', groupTypeName).group(1)
        cachedGroups[acronym.text] = { 'id': object.find('id').text, 'name': object.find('name').text, 'type': groupType}


# Loop for all active WG
for group in cachedGroups:
    if (cachedGroups[group]['type'] != 'wg'):
        continue
    # This is an active WG, get all the chairs
    getMembers(group, 'chair')

with open('wgchairs.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)

with open('wgchairs.js', 'w', encoding = 'utf-8') as f:
    f.write("var wgChairs = ")
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar wgChairsCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))
