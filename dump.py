#!env python3

#Copyright 2021-2021 Eric Vyncke
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import json
import sys
import zlib
from base64 import b64decode, standard_b64decode, b64encode, urlsafe_b64decode
import base64
from datetime import date, datetime
import urllib.request

import cbor2
from binascii import unhexlify, hexlify

def hexDump(s, backgroundColor = None, offset = None, length = None):
    i = 0
    while i < len(s):
        j = 0
        while i + j < len(s) and j < 16:
            if backgroundColor and offset <= i+j and i+j < offset+length:
                print('<span style="background-color: {};">'.format(backgroundColor), end = '')
            if isinstance(s[i+j], str):
                print('{:02X} '.format(ord(s[i+j])), end = '')
            else:
                print('{:02X} '.format(s[i+j]), end = '')
            if backgroundColor and offset <= i+j and i+j < offset+length:
                print('</span>', end = '')
            j += 1
        while j < 16:
            print("   ", end = '')
            j += 1
        print("   ", end = '')
        j = 0
        while i < len(s) and j < 16:
            if isinstance(s[i], str):
                c = ord(s[i])
            else:
                c = s[i]
            if backgroundColor and offset <= i and i < offset+length:
                print('<span style="background-color: {};">'.format(backgroundColor), end = '')
            if (32 <= c and c <= 127):
                print(chr(c) + ' ', end='')
            else:
                print('. ', end = '')
            if backgroundColor and offset <= i and i < offset+length:
                print('</span>', end = '')
            i += 1
            j += 1
        print()

def hexDump1Line(s):
    i = 0
    result = "0x"
    while i < len(s):
        result += '{:02X}'.format(s[i])
        i += 1
    return result

def numericModeDecode(s):
    i = 0
    result = bytearray()
    while i+1 < len(s):
        c = int(s[i]) * 10 + int(s[i+1]) + ord('-')
        result.append(c)
        i += 2
    return result

