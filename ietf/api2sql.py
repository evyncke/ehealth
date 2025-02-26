#!/usr/bin/env python3

#Copyright 2024 Eric Vyncke evyncke@cisco.com

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
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="uietf",
  password="FTEI",
  database="ietf"
)
# mydb.raise_on_warnings = True
mycursor = mydb.cursor()
# Let's prepare for very dumb names
mycursor.execute('SET NAMES utf8mb4;')
mycursor.execute('SET CHARACTER SET utf8mb4;')
mycursor.execute('SET character_set_connection=utf8mb4;')

baseURI = 'https://datatracker.ietf.org/api/v1/'

schemas = []

class Column:
    def __init__(self, tagName, verboseName, SQLName, SQLType):
        self.tagName = tagName
        self.verboseName = verboseName
        self.SQLName = SQLName 
        self.SQLType = SQLType

class Schema:
    def __init__(self, name, schemaURI, tableName):
        self.name = name
        self.schemaURI = schemaURI
        self.tableName = tableName
        self.columns = []

    def addColumn(self, column):
        self.columns.append(column) 

def schema2Table(group):
    tableName = group.replace('/', '_')
    schemaURI = baseURI + group + '/schema/?format=xml'
    print('Creating ' + tableName + ' based on ' + schemaURI)
    schemaTree = etree.parse(request.urlopen(schemaURI))
    schemaRoot = schemaTree.getroot()
    sqlStatement = "CREATE TABLE IF NOT EXISTS " + tableName + " (" 
    mycursor.execute("DROP TABLE IF EXISTS " + tableName)
    sqlStatement = "CREATE TABLE " + tableName + " (" 
    primaryKeys = ''
    firstColumn = True 
    schema = Schema(group, schemaURI, tableName)
    for field in schemaRoot.find('fields'):
        type = field.find('type').text
        SQLType = 'unsupported'
        match type:
            case 'integer': 
                SQLType = 'int'
            case 'string': 
                SQLType = 'varchar(255)'
            case 'boolean': 
                SQLType = 'boolean'
            case 'datetime': 
                SQLType = 'datetime'
            case '_':
                SQLType = 'unsupported'
        if (SQLType == 'unsupported'):
            continue
        # object name if not verbose but rather the name of the field
        tagName = field.tag
        SQLName = tagName
        verboseName = field.find('verbose_name').text.replace(' ', '_').replace('(', '_'). replace(')', '_')
        # SQLName = verboseName
        match verboseName:
            case 'desc':
                SQLName = 'description' # Desc is a reserved word in SQ
            case 'order':
                SQLName = 'item_order' # Order is a reserved word in SQL  
        schema.addColumn(Column(tagName, verboseName, SQLName, SQLType))      
        primaryKey = field.find('primary_key').text
        if (primaryKey == 'True'):
            SQLType += ' NOT NULL'
            primaryKeys += ' ' + verboseName
        if (not firstColumn):
            sqlStatement += ', '
        else:
            firstColumn = False
        sqlStatement += SQLName + ' ' + SQLType
    if (primaryKeys != ''):
        sqlStatement += ', PRIMARY KEY(' + primaryKeys + ') ' 
    sqlStatement += ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'
    print(sqlStatement)
    mycursor.execute(sqlStatement)
    return schema

def fillTable(groupSchema):
    print("Inserting data in " + groupSchema.tableName)
    nextUri= '/api/v1/' + groupSchema.name + "/?format=xml&limit=100&offset=0"
    # Prepare SQL statement
    cols = []
    values = []
    for column in groupSchema.columns:
        cols.append(column.SQLName)
        values.append('%s')
    sql = "INSERT INTO " + groupSchema.tableName + " (" + ', '.join(cols) + ') VALUES (' + ', '.join(values) + ')'
    print("Prepared SQL statement", sql)
    while (nextUri):
        url = "https://datatracker.ietf.org" + nextUri
        print("Fetching", url)
        tree = etree.parse(request.urlopen(url))
        root = tree.getroot()
        meta = root.find('meta')
        nextUri = meta.find('next').text
        objects = root.find('objects')
        for object in objects:
            # Now let's process a single object, assuming that all SQL rows will have a value
            values = []
            for column in groupSchema.columns:
                if (object.find(column.tagName) is None):
                    continue
                cols.append(column.SQLName)
                if (object.find(column.tagName).text is None):
                    values.append(None)
                else:
                    match column.SQLType:
                        case 'varchar(255)': 
                            values.append(object.find(column.tagName).text[:200]) # Some UTF-8 characters takes more than one byte...
                        case 'datetime': 
                            values.append(object.find(column.tagName).text.replace('T', ' ').replace('Z', ''))
                        case 'int': 
                            values.append(object.find(column.tagName).text)
                        case 'boolean': 
                            if (object.find(column.tagName).text == 'True'):
                                values.append(1)
                            else:
                                values.append(0)
            print(sql)
            print(values)
            mycursor.execute(sql, values)
        mydb.commit()
        print(mycursor.rowcount, "record inserted into ", groupSchema.tableName)

def importData(group):
    print("Importing: " + group)
    # Create table based on the group schema
    groupSchema = schema2Table(group)
    # Fill in the table
    fillTable(groupSchema)


#importData('group/group')
#importData('person/alias')
#importData('doc/documentauthor')
#importData('doc/document')
#importData('doc/statetype')
#importData('person/historicalperson')
#importData('group/groupevent')
#importData('person/person')
#importData('submit/submission') # Beware this contains more than 100.000 entries.... not to be reimported dumbly...
#importData('nomcom/volunteer')
#importData('nomcom/nomcom')

mycursor.close()
mydb.close()
