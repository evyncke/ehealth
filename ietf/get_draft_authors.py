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
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import ast
import json

cachedPersons = {}
backInTime = date.today() + relativedelta(months=-4)

# Read all recent submission (4 months old max)
nextUri= "/api/v1/submit/submission/?submission_date__gte=" + str(backInTime) + "&format=xml&limit=100&offset=0"
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    objects = root.find('objects')
    for object in objects:
        state = object.find('state') 
        if not state.text == '/api/v1/name/draftsubmissionstatename/posted/':
            continue
        authors = ast.literal_eval(object.find('authors').text)
        # JSON encoded array of object authors including email and name and affiliation, let's use email as the key
        for author in authors:
            authorObject = { 'name' : author['name'] } ;
            if author['affiliation']:
                    authorObject['affiliation'] = author['affiliation'] ;
            cachedPersons[author['email']] = authorObject ;


with open('draftauthors.json', 'w', encoding = 'utf-8') as f:
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)

with open('draftauthors.js', 'w', encoding = 'utf-8') as f:
    f.write("var draftAuthors = ")
    json.dump(cachedPersons, f, ensure_ascii = False, indent = 2)
    f.write(";")
    now = datetime.datetime.now(datetime.timezone.utc)
    f.write("\nvar draftAuthorsCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))
