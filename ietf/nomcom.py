#!/usr/bin/env python3

#Copyright 2025 Eric Vyncke evyncke@cisco.com

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

    # Define the mapping dictionary
canonical_mappings = {
        "akayla": "AKAYLA",
        "apnic": "APNIC",
        "apple": "Apple",
        "arin": "ARIN",
        "china mobile" : "China Mobile",
        "cisco": "Cisco",
        "comcast": "Comcast",
        "f5": "F5",
        "facebook": "Facebook",
        "futurewei": "Futurewei",
        "google": "Google",
        "hewlett packard": "HPE",
        "huawei": "Huawei",
        "icann": "ICANN",
        "independent": "Independent",
        "juniper": "Juniper",
        "microsoft": "Microsoft",
        "mozilla": "Mozilla",
        "nokia": "Nokia",
        "no": "Independent",
        "none": "Independent",
        "ripe": "RIPE",
        "self": "Independent",
        "zte": "ZTE",
        # Add more mappings as needed
}

def get_largest_nomcom_id():
    url = "https://datatracker.ietf.org/api/v1/nomcom/nomcom/?format=json&order_by=-id&limit=1"
    with request.urlopen(url) as resp:
        payload = json.load(resp)
        objects = payload.get("objects", [])
        if not objects:
            return None
        return objects[0].get("id")

thisNomCom =  get_largest_nomcom_id()

def get_canonical_form(input_string):
    """
    Maps an input string to its canonical form based on a predefined dictionary.

    Parameters:
        input_string (str): The string to be mapped to its canonical form.

    Returns:
        str: The canonical form if found in the dictionary, otherwise the original input string.
    """

    # Normalize the input string (e.g., lowercase and strip whitespace)
    normalized_input = input_string.strip().lower()

    # Look for the canonical form in the dictionary
    for canonical_key in canonical_mappings:
        if normalized_input.startswith(canonical_key):
            return canonical_mappings[canonical_key]
        
    return input_string

def getPerson(uri, affiliation, time):
# uri looks like api/v1/person/person/111656/ with elements such as ascii, biography, id, name, resource_uri, time, ... but no email :-(
    url =  "https://datatracker.ietf.org" + uri + '?format=xml'
    personTree = etree.parse(request.urlopen(url))
    personRoot = personTree.getroot()
    ascii = personRoot.find('ascii').text
    print("{}; {}; {}".format(affiliation, ascii, time))

nextUri = "/api/v1/nomcom/volunteer/?format=xml&limit=50&offset=0&nomcom=" + str(thisNomCom)
perAffiliation = {}
while (nextUri):
    url = "https://datatracker.ietf.org" + nextUri
    tree = etree.parse(request.urlopen(url))
    root = tree.getroot()
    meta = root.find('meta')
    nextUri = meta.find('next').text
    totalCount = meta.find('total_count').text
#    print("Got {} entries".format(totalCount))
    objects = root.find('objects')
    for object in objects:
        nomComId = object.find('nomcom').text
        if nomComId != '/api/v1/nomcom/nomcom/' + str(thisNomCom) + '/':
            print('skipping wrong nomcom', nomComId)
            continue
        personId = object.find('person').text
        volunteerId = object.find('resource_uri').text
        affiliation = object.find('affiliation').text
        if affiliation is not None:
            affiliation = get_canonical_form(affiliation)
            if affiliation in perAffiliation:
               perAffiliation[affiliation] += 1
            else:
               perAffiliation[affiliation] = 1
        time = object.find('time').text
        getPerson(personId, affiliation, time)

with open('data/nomcom.json', 'w', encoding = 'utf-8') as f:
    json.dump(perAffiliation, f, ensure_ascii = False, indent = 2)
