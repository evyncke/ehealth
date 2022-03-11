#!env python3

#Copyright 2021-2022 Eric Vyncke
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
import datetime
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

from dump import hexDump, hexDump1Line, numericModeDecode

def verify(cin):
    hexDump(cin, 'orange', 0, 1)
    parts = cin.split('.')
    print("\nThe QR-code contains dots and starts with a '0' or a '1',this seems to be the weird Australian Jason Web Token (JWT) in 4 (!) parts:<ul>")
    print("<li><b>Removed/Fake JWT header</b>: {}</li>".format(parts[0]))
    print("<li><b>Base64 encoded JWT payload</b>, once decoded and pretty printed for JSON:")
    payload = urlsafe_b64decode(parts[1] + '==').decode('UTF-8')
    hexDump(payload)
    print(json.dumps(json.loads(payload), indent=4))
    print("</li>")
    print("<li><b>Base64 encoded JWT signature</b>, once decoded:")
    trailer = urlsafe_b64decode(parts[2] + '==')
    hexDump(trailer)
    print("</li>")
    trailer = urlsafe_b64decode(parts[3] + '==').decode('ASCII')
    print("<li><b>Base64 encoded trailer (not part of JWT)</b>, once decoded: {}".format(trailer))
    trailer_parts = trailer.split('.')
    print("<ul>")
    print("<li><b>Type</b>: {}</li>".format(trailer_parts[0]))
    print("<li><b>ID (unknown semantics)</b>: {}</li>".format(trailer_parts[1]))
    date = datetime.datetime.fromtimestamp(int(trailer_parts[2]))
    print("<li><b>Timestamp</b>: {} ({})</li>".format(trailer_parts[2], date))
    print("</ul>")
    print("</li>")
    print("</ul>")
