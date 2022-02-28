#!/usr/bin/env python3

from lxml import etree
from urllib import request
from datetime import date
from dateutil.relativedelta import relativedelta
import ast
import json

cachedPersons = {}
backInTime = date.today() + relativedelta(months=-4)

# Read all recent submission (4 months old max)
nextUri= "/api/v1/submit/submission/?submission_date__gte=" + str(backInTime) + "&format=xml&limit=100&offset=0"
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    print("Getting", url)
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    objects = root.find('objects')
    for object in objects:
        state = object.find('state') 
        if not state.text == '/api/v1/name/draftsubmissionstatename/posted/':
#            print(object.find('state').text, object.find('name').text)
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
