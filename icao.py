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

from dump import hexDump, hexDump1Line, numericModeDecode

def verify(cin, json_object):
    hexDump(cin)
    print("\nThis is a JSON encoded object, let's pretty print it:\n")
    print(json.dumps(json_object, indent=4))
    if not ('data' in json_object and 'sig' in json_object):
        print("\n<span style=\"background-color: red;\">Alas, this JSON object is not recognized...</span>")
        sys.exit(-1)
    print("\nIt is probably the International Civil Aviation Organization (ICAO) Visible Data Seal (VDS) format. Let's try to analyse it based on: <a href=\"https://www.icao.int/Security/FAL/TRIP/PublishingImages/Pages/Publications/Visible%20Digital%20Seal%20for%20non-constrained%20environments%20%28VDS-NC%29.pdf\">the ICAO specifications</a>. With two top objects:")
    print("<ul><li><b>data</b>: the actual data;</li>")
    print("<li><b>sig</b>: the signature and the associated the X.509 certificate in <b>cer</b>.</li></ul>\n")
    print("Let's first analyse the <b>sig</b> parts where the <b>sig</b>nature and <b>cer</b>tificate parts are base64 encoded. After decoding the base64 of the certificate, it is now:")
    cert_b64 = json_object['sig']['cer']
    cert_der = urlsafe_b64decode(cert_b64+ '==')  # Add two = as Python will silently discard them if there are too many '='
    hexDump(cert_der)
    cert = x509.load_der_x509_certificate(cert_der)
    public_key = cert.public_key()
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        key_type = 'Elliptic Curve'
    else:
        key_type = 'unsupported key type'
    print("\nThe X.509 certificate of the VDS signer has the following properties:<ul>")
    print("<li><b>Issuer</b>: {}</li>".format(cert.issuer.rfc4514_string()))
    print("<li><b>Subject</b>: {}</li>".format(cert.subject.rfc4514_string()))
    print("<li><b>Not valid before</b>: {}</li>".format(cert.not_valid_before))
    print("<li><b>Not valid after</b>: {}</li>".format(cert.not_valid_after))
    print("<li><b>Public key ({})</b>: {}</li>".format(key_type, public_key))
    print("</ul>")
    print('end')
