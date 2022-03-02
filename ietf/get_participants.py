#!/usr/bin/env python3

from lxml import etree, html
from urllib import request
import json
import datetime 

url = "https://registration.ietf.org/113/participants/onsite/"

countries = {}
participants = []

root = html.parse(request.urlopen(url))
print("var participantsOnsite = [")
rows = root.iter('tr')
next(rows) # Skip the header
for row in rows:
        print('["{}", "{}", "{}", "{}"],'.format(row[0].text, row[1].text, row[2].text, row[3].text))
        participants.append([row[0].text, row[1].text, row[2].text, row[3].text])
        country = row[3].text
        if country in countries:
            countries[country] = countries[country] + 1
        else:
            countries[country] = 1
print("] ;")

print("var countries = ")
print(json.dumps(countries))
print(";")

with open('onsite.json', 'w', encoding = 'utf-8') as f:
        json.dump(participants, f, ensure_ascii = False, indent = 2)

# Look for remote participants
url = "https://registration.ietf.org/113/participants/remote/"

participants = []
root = html.parse(request.urlopen(url))
print("var participantsRemote = [")
rows = root.iter('tr')
next(rows) # Skip the header
for row in rows:
        print('["{}", "{}", "{}", "{}"],'.format(row[0].text, row[1].text, row[2].text, row[3].text))
        participants.append([row[0].text, row[1].text, row[2].text, row[3].text])
print("] ;")

with open('remote.json', 'w', encoding = 'utf-8') as f:
        json.dump(participants, f, ensure_ascii = False, indent = 2)

now = datetime.datetime.now(datetime.timezone.utc)
print("var registrationCollectionDate = '{}';".format(now.isoformat(timespec='seconds')))

