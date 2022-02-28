#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright 2020, Eric Vyncke, evyncke@cisco.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
   
# Typically done after rsync -avtz --delete --exclude '*.txt' --exclude '*.notprepped.xml' ftp.rfc-editor.org::rfcs-text-only /tmp/rfc-cache 
   
from xml.dom import minidom, Node
import xml.dom
from pprint import pprint
import sys, getopt
import io, os, glob, re
import zipfile
import tempfile, datetime
import urllib.request

# Same states to be kept
rfcDate = None
rfcAuthors = []
rfcTitle = None
rfcMonth = None
nowMonth = datetime.datetime.now().month
nowYear = datetime.datetime.now().year
rfcYear = None
seriesInfoString = None

def printTree(front):
	print('All children:')
	for elem in front.childNodes:
		if elem.nodeType == Node.TEXT_NODE:
			print("\t TEXT: '", elem.nodeValue, "'")
		if elem.nodeType != Node.ELEMENT_NODE:
			continue
		print("\t", elem.nodeName)
		print("\tAttributes:")
		for i in range(elem.attributes.length):
			attrib = elem.attributes.item(i)
			print("\t\t", attrib.name, ' = ' , attrib.value)
		print("\tChildren:")
		for child in elem.childNodes:
			if child.nodeType == Node.ELEMENT_NODE:
				print("\t\tELEMENT: ",child.nodeName)
			elif child.nodeType == Node.TEXT_NODE:
				print("\t\tTEXT: ", child.nodeValue)
	print("\n----------\n")

	
def parseAuthor(elem):	# Per https://tools.ietf.org/html/rfc7991#section-2.7
	global rfcAuthors

	# looking for the organization element as in https://tools.ietf.org/html/rfc7991#section-2.35 that can only contain text
	organization = ''
	email = ''
	for child in elem.childNodes:
		if child.nodeType != Node.ELEMENT_NODE:
			continue
		elif child.nodeName == 'organization':
			for grandchild in child.childNodes:
				if grandchild.nodeType == Node.TEXT_NODE:
					organization = ' ' + grandchild.nodeValue	
		elif child.nodeName == 'address':
			for grandchild in child.childNodes:
				if grandchild.nodeName == 'email':
					for grandgrandchild in grandchild.childNodes:
						if grandgrandchild.nodeType == Node.TEXT_NODE:
							email = ' ' + grandgrandchild.nodeValue
	# Is it from Cisco ?
	if not ('cisco.com' in email or 'cisco' in organization or 'meraki' in organization or 'meraki.com' in organization):
		return

	if elem.hasAttribute('asciiFullname'):
		authorName = elem.getAttribute('asciiFullname')
	elif elem.hasAttribute('fullname'):
		authorName = elem.getAttribute('fullname')
	else:
		authorName = ''
		if elem.hasAttribute('initials'):
			authorName = author + elem.getAttribute('initials') + ' '
		if elem.hasAttribute('surname'):
			authorName = authorName + elem.getAttribute('surname')
	rfcAuthors.append("{name}; {email}".format(name = authorName, email = email))

def parseDate(elem):
	global rfcDate, rfcMonth, rfcYear
	
	dateString = ''
	rfcMonth = None
	rfcYear = None
	if elem.hasAttribute('day'):
		dateString = elem.getAttribute('day') + ' '
	if elem.hasAttribute('month'):
		dateString = dateString + elem.getAttribute('month') + ' '
		rfcMonth = int(elem.getAttribute('month'))
	if elem.hasAttribute('year'):
		dateString = dateString + elem.getAttribute('year')
		rfcYear = int(elem.getAttribute('year'))
	if dateString != '':
		rfcDate = dateString

def parseFront(elem):	
	if elem.nodeType != Node.ELEMENT_NODE:
		return
	for child in elem.childNodes:
		if child.nodeType != Node.ELEMENT_NODE:
			continue
		elif child.nodeName == 'author':
			parseAuthor(child)
		elif child.nodeName == 'date':
			parseDate(child)
		elif child.nodeName == 'seriesInfo':
			parseSeriesInfo(child)
		elif child.nodeName == 'title':
			parseTitle(child)

# TODO handle wrongly formatted    <seriesInfo name="Internet-Draft" value="draft-ietf-anima-autonomic-control-plane-29"/>
def parseSeriesInfo(elem):
	global seriesInfoString

	seriesInfoString = ''
	if elem.hasAttribute('name'):
		seriesInfoString = elem.getAttribute('name')
	if elem.hasAttribute('value'):
		seriesInfoString = seriesInfoString + elem.getAttribute('value') 
	
def parseTitle(elem):
	global rfcTitle
	
	textValue = ''
	for text in elem.childNodes:
		if text.nodeType == Node.TEXT_NODE:
			textValue += text.nodeValue
	rfcTitle = textValue 
							

def processRFCXML(inFilename):
	global xmldoc
	global rfcAuthors
	global rfcYear, nowYear, rfcMonth, nowMonth, monthsBack
	
	if os.path.isfile(inFilename):
		xmldoc = minidom.parse(inFilename)
	else:
		try:
			response = urllib.request.urlopen('https://tools.ietf.org/id/' + inFilename + '.xml')
		except:
			print("Cannot fetch the XML document from the IETF site...")
			sys.exit(1)
		draftString = response.read()
		xmldoc = minidom.parseString(draftString)
		print("Fetching the RFC from the IETF site...")

	if len(xmldoc.getElementsByTagName('rfc')) != 1:
		print("Cannot process {}: no RFC element".format(inFilename))
		return

	rfc = xmldoc.getElementsByTagName('rfc')[0]	
	front = rfc.getElementsByTagName('front')[0]

	rfcAuthors = []
	parseFront(front)

	# Check if not too old
	if (12 * (nowYear - rfcYear) + nowMonth - rfcMonth) >  monthsBack:
		return

	for author in rfcAuthors:
		print("{author}; {rfcid}; {date}; {title}".format(author=author, rfcid=seriesInfoString, date=rfcDate, title=rfcTitle))

if __name__ == '__main__':
	inFilename = None 
	inDirectory = None
	monthsBack = 3
	try:
		opts, args = getopt.getopt(sys.argv[1:],"d:hi:m:",["ifile=", "directory", "months"])
	except getopt.GetoptError:
		print('xml2docx.py [--months <months back>] [--ifile <inputfile>  | --directory <inputfiles directory>]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('ciscoAuthors.py -i <inputfile/draft-name> -d <directory> -m <months back in time>')
			sys.exit()
		elif opt in ("-d", "--directory"):
			inDirectory = arg
		elif opt in ("-i", "--ifile"):
			inFilename = arg
		elif opt in ("-m", "--months"):
			monthsBack = int(arg)

	if inFilename == None and inDirectory == None:
		print('Missing input filename or directory')
		sys.exit(2)
	if inFilename:
		processRFCXML(inFilename)

	for f in glob.glob(inDirectory + '/*.xml'):
		if re.match(r'.*rfc.*.\.xml', f):
			processRFCXML(f)
