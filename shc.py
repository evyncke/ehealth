#!env python3

# - some more explanations on the flight
# - generating HTML code
# For those parts:
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

from base45 import b45decode

import cose
from cose.keys.curves import P256
from cose.algorithms import Es256, EdDSA, Ps256
from cose.headers import KID
from cose.keys import CoseKey
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN
from cose.keys.keyparam import KpKty
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.messages import CoseMessage
import cose.exceptions
from cryptography.utils import int_to_bytes
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from cryptography import x509

from dump import hexDump, numericModeDecode

def verify(cin):
    hexDump(cin, 'orange', 0, 5)
    print("\nIt looks like a <a href='https://www.iana.org/assignments/uri-schemes/prov/shc'>SHC</a> URI.")
    cin = cin[5:]
    print("Based on the <a href='https://spec.smarthealth.cards/'>specifications</a> as they are open thanks to SMART&reg; Health.")
    print("\nDecoding the Numeric Mode QR...")
    cin = numericModeDecode(cin)
    hexDump(cin)
    # Should raise an exception if cin.count('.') != 2
    print("\nThis should be JSON Web Signature (JWS) <a href='https://datatracker.ietf.org/doc/html/rfc7515'>RFC7515</a> format where the protected header, the payload, and the signature are separated by a '.' character.")
    dot_index1 = cin.find(ord('.'))
    dot_index2 = cin.rfind(ord('.'))
    print("Let's split this in three parts based on the '.' character at offsets {} and {}.".format(dot_index1, dot_index2))
    phdr =  cin[:dot_index1]
    print("\nJWS Protected header:")
    hexDump(phdr)
    payload =  cin[dot_index1+1:dot_index2]
    print("\nJWS Payload:")
    hexDump(payload)
    signature =  cin[dot_index2+1:]
    print("\nJWS Signature:")
    hexDump(signature)
    print("\nAll those 3 parts are base64 encoded (without the trailing '=' used for padding), let's decode them...")
    phdr = base64.urlsafe_b64decode(phdr.decode('ASCII') + '==')  # Add two = as Python will silently discard them if there are too many '='
    print("\nBase64 decoded JWS Protected header:")
    hexDump(phdr)
    phdr_json = json.loads(phdr)
    print("\nOr a pretty print of the JSON content of the JWS protected header:")
    print(json.dumps(phdr_json, indent=4))
    payload = base64.urlsafe_b64decode(payload.decode('ASCII') + '==')  # Add two = as Python will silently discard them if there are too many '='
    print("\nBase64 decoded JWS Payload:")
    hexDump(payload)
    signature = base64.urlsafe_b64decode(signature.decode('ASCII') + '==')  # Add two = as Python will silently discard them if there are too many '='
    print("\nBase64 decoded JWS Signature (i.e., the {}-bit hash representing the signature):".format(len(signature)*8))
    hexDump(signature)
    # Should check whether phdr contains "zip": "DEF" to DEFLATE it
    print("\nThe JWS payload is compressed using '<a href='https://datatracker.ietf.org/doc/html/rfc1951'>deflate</a>' (as the protected header contains a 'zip' key with 'DEF' value), let's uncompress it")
    payload = zlib.decompress(payload, wbits = -15)  # wbits = −8 to −15: Uses the absolute value of wbits as the window size logarithm. The input must be a raw stream with no header or trailer.
    hexDump(payload)
    print("\nOr a pretty print of the JSON content of the JWS payload:")
    payload_json = json.loads(payload.decode('ASCII'))
    print(json.dumps(payload_json, indent=4))
