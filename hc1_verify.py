#!env python3

# Heavily based on https://github.com/ehn-dcc-development/ehn-sign-verify-python-trivial
# under https://github.com/ehn-dcc-development/ehn-sign-verify-python-trivial/blob/main/LICENSE.txt
# It looks like public keys are at
DEFAULT_TRUST_URL = 'https://verifier-api.coronacheck.nl/v4/verifier/public_keys'
DEFAULT_TRUST_UK_URL = 'https://covid-status.service.nhsx.nhs.uk/pubkeys/keys.json'

# Main additions by eric@vyncke.org:
# - support for US SMART Health Card
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

import shc
import icao
import australia
from dump import hexDump, hexDump1Line, numericModeDecode

def add_kid(kid_b64, key_b64):
        kid = b64decode(kid_b64)
        asn1data = b64decode(key_b64)
        # value of subjectPk is a base64 ASN1 package of:
        #  0:d=0  hl=2 l=  89 cons: SEQUENCE          
        #      2:d=1  hl=2 l=  19 cons: SEQUENCE          
        #      4:d=2  hl=2 l=   7 prim: OBJECT            :id-ecPublicKey
        #     13:d=2  hl=2 l=   8 prim: OBJECT            :prime256v1
        #     23:d=1  hl=2 l=  66 prim: BIT STRING 
        pub = serialization.load_der_public_key(asn1data)
        if (isinstance(pub, RSAPublicKey)):
            kids[kid_b64] = CoseKey.from_dict(
                {   
                    KpKty: KtyRSA,
                    KpAlg: Ps256,  # RSSASSA-PSS-with-SHA-256-and-MFG1
                    RSAKpE: int_to_bytes(pub.public_numbers().e),
                    RSAKpN: int_to_bytes(pub.public_numbers().n)
                })
        elif (isinstance(pub, EllipticCurvePublicKey)):
            kids[kid_b64] = CoseKey.from_dict(
                {
                    KpKty: KtyEC2,
                    EC2KpCurve: P256,  # Ought o be pk.curve - but the two libs clash
                    KpAlg: Es256,  # ecdsa-with-SHA256
                    EC2KpX: pub.public_numbers().x.to_bytes(32, byteorder="big"),
                    EC2KpY: pub.public_numbers().y.to_bytes(32, byteorder="big")
                 })
        else:
            print(f"Skipping unexpected/unknown key type (keyid={kid_b64}, {pub.__class__.__name__}).",  file=sys.stderr)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

BASE45_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
def verifyBase45(s):
    i = 0
    while i < len(s):
        if s[i] not in BASE45_CHARSET:
            print("Invalid base45 character found: '{}' == 0x{:2X}.".format(s[i], ord(s[i])))
            return i
        i += 1
    return -1

# Load the .JSON files into dictionnary

def loadJson(fn):
    result = {}
    with open(fn) as jsonFile:
        dict = json.load(jsonFile)
    for value in dict['valueSetValues']:
        result[value] = dict['valueSetValues'][value]['display']
    return result

def decode(dict, key):
    if key in dict:
        return dict[key]
    return "unknown/" + key

country = loadJson('country-2-codes.json') # for v/co
disease = loadJson('disease-agent-targeted.json') # for v/tg
vaccine_manufacturer = loadJson('vaccine-mah-manf.json') # for v/ma
vaccine_product = loadJson('vaccine-medicinal-product.json') # for v/mp
test_type = loadJson('test-type.json') # for t/tt
test_manf = loadJson('test-manf.json') # for t/ma
test_result = loadJson('test-result.json') # for t/tr

kids = {}
keyid = None
key = None

# Let's try to load the public keys
url = DEFAULT_TRUST_URL
response = urllib.request.urlopen(url)
pkg = json.loads(response.read())
payload = b64decode(pkg['payload'])
trustlist = json.loads(payload)
# 'eu_keys': {'hA1+pwEOxCI=': [{'subjectPk': 'MFkwEw....yDHm7wm7aRoFhd5MxW4G5cw==', 'keyUsage': ['t', 'v', 'r']}],
eulist = trustlist['eu_keys']
for kid_b64 in  trustlist['eu_keys']:
    add_kid(kid_b64,eulist[kid_b64][0]['subjectPk'])
# And now for UK
url = DEFAULT_TRUST_UK_URL
response = urllib.request.urlopen(url)
uklist = json.loads(response.read())
for e in uklist:
    add_kid(e['kid'], e['publicKey'])

cin = sys.stdin.buffer.read().strip()

if len(cin) == 0:
    print('The QR-code could not be detected in the image')
    sys.exit(-1)

print("\nAfter analyzing the uploaded image, the QR code is (left-hand column is the hexadecimal/computer format, the right-hand column is the ASCII/human format):")
cin = cin.decode("ASCII")

if cin.startswith('shc:/'):
    shc.verify(cin)
    sys.exit(-1)

if cin.startswith('HC1'):
    hexDump(cin, 'orange', 0, 3)
    print("\nThe <span style=\"background-color: orange;\">'HC1:'</span> signature is found in the first characters, 'HC1' stands for Health Certificate version 1. Let's remove it...") ;
    cin = cin[3:]
    if cin.startswith(':'):
        cin = cin[1:]
else:
    try:
        json_object = json.loads(cin)
    except:

        if cin.count('.') == 3 and (cin.startswith('0.') or cin.startswith('1.')):   # The weird Australian Jason Web Token https://medium.com/@wabz/reversing-service-nsws-digital-driver-licence-f55123d7c220
            australia.verify(cin)
            sys.exit(-1)

        print("\n<span style=\"background-color: red;\">Alas, this QR code is not recognized...</span>")
        hexDump(cin)

        print("\nTrying to base64 decode...")
        try:
            cin = urlsafe_b64decode(cin)
            print("\nAfter base64 decode:")
            hexDump(cin)
            print(hexDump1Line(cin))
        except:
            print("Message was not base64 encoded")

        print("\nTrying to interpret a DER-encoded X509 certificate...")
        try:
            cert = x509.load_der_x509_certificate(cin)
            print("... it is indeed a DER-encoded certificate")
            print(cert)
        except:
            print("It is not a X.509 certificate...")
        print("\nTrying to interpret as CBOR encoded...")
        try:
            cbor_object = cbor2.loads(cin)
            print("... success")
            print(cbor_object)
        except:
            print("It is not CBOR encoded...")
        print("That's all folks !")
        sys.exit(-1)
    
    # Probably the ICAO format https://www.icao.int/Security/FAL/TRIP/PublishingImages/Pages/Publications/Visible%20Digital%20Seal%20for%20non-constrained%20environments%20%28VDS-NC%29.pdf
    icao.verify(cin, json_object)
    sys.exit(-1)

try:
    cin = b45decode(cin)
except ValueError:
    print("\nWhile the QR-code should contain a base45 string, it does not at offset",verifyBase45(cin), "out of", len(cin), "characters. Cannot proceed... please upload a valid QR-code")
    sys.exit(-1)

print("\nA QR-code only allows for 45 different characters (letters, figures, some punctuation characters)... But the health certificate contains binary information, so, this binary information is 'encoded' in base45 (thanks to my friend Patrik's IETF draft <a href='https://datatracker.ietf.org/doc/html/draft-faltstrom-base45-06'>draft-faltstrom-base45</a>).")
print("Base45 decoding... The decoded message is now (many more binary characters represented as '.' on the right-hand column and also less octects):")
if cin[0] == 0x78:
    hexDump(cin, backgroundColor='lightblue', offset = 0, length = 1)
else:
    hexDump(cin)

if cin[0] == 0x78:
    len_before = len(cin)
    cin = zlib.decompress(cin)
    len_after = len(cin)
    print("\nThe first octet is <span style=\"background-color: lightblue;\">0x78</span>, which is a sign for ZLIB compression. After decompression, the length went from {} to {} octets:".format(len_before, len_after))
    if len_before >= len_after:
        print("Obviously, in this case, the compression was rather useless as the 'compressed' length is larger than the 'uncompressed' one... Compression efficiency usually depends on the text.")
    hexDump(cin, backgroundColor="yellow", offset=0, length=1)

msb_3_bits = cin[0] >> 5
if msb_3_bits == 6:
    msb_type = 'tag'
else:
    msb_type = 'unexpected type'
lsb_5_bits = cin[0] & 0x1F

print("\nInterpreting the message as Concise Binary Object Representation (CBOR), another IETF standards by my friends Carsten and Paul <a href='https://datatracker.ietf.org/doc/html/rfc7049'>RFC 7049</a>... ", end = '')
print("The first byte is <span style=\"background-color: yellow;\">{:2X}</span> and is encoded as follow:".format(cin[0]))
print(" - most significant 3 bits == {:2X}, which is a {};".format(msb_3_bits, msb_type))
print(" - least significant 5 bits == {} == 0x{:2X}.".format(lsb_5_bits, lsb_5_bits))
if cbor2.loads(cin).tag != 18:
    raise Exception("This is not a COSE message!")
print("As CBOR tag is 18 == 0x12 (see IANA <a href='https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml'>registry</a>), hence it is a CBOR Object Signing and Encryption (COSE) Single Signer Data Object message, another IETF standards by late Jim Schaad <a href='https://datatracker.ietf.org/doc/html/rfc8152'>RFC 8152</a>")

print("\nChecking the COSE structure (ignoring the signature) of the CBOR Web Token (yet another IETF standards <a href='https://datatracker.ietf.org/doc/html/rfc8392'>RFC 8392</a>)...")
try:
    decoded = CoseMessage.decode(cin)
except cose.exceptions.CoseException as e:
    print("This is not a recognized COSE data object:", e)
    sys.exit(-1)

key = None 
if cose.headers.KID in decoded.phdr.keys():
        print("\tCOSE Key Id(KID):", hexDump1Line(decoded.phdr[cose.headers.KID]), "(KID is the first 8 bytes of the SHA256 of the certificate, list of trusted KIDs is at <a href='https://verifier-api.coronacheck.nl/v4/verifier/public_keys'>https://verifier-api.coronacheck.nl/v4/verifier/public_keys</a>).") 
        key = b64encode(decoded.phdr[cose.headers.KID]).decode('ASCII') # Unsure why... possible to make it canonical before using it as an index
        if not key in kids:
            print("\t<span style=\"color: red;\">!!! This KeyId  is unknown  -- cannot verify!!!</span>")
        else:
            key  = kids[key]
            print("\t\tThis key is trusted from {} or {}".format(DEFAULT_TRUST_URL, DEFAULT_TRUST_UK_URL))
            decoded.key = key
            if decoded.verify_signature():
                print("\t\t<span style=\"color: green;\">And the COSE signature is verified => this digital green certificate is valid.</span>")
            else:
                print("\t\t<span style=\"color: red;\">!!! Tthe COSE signature is INVALID => this digital green certificate is <b>NOT</b>valid !!!</span>")

if cose.headers.Algorithm in decoded.phdr.keys():
        algorithm = decoded.phdr[cose.headers.Algorithm]
        if algorithm == cose.algorithms.Es256:
            algorithm = 'Es256 (ECDSA w/ SHA-256)'
        elif algorithm == cose.algorithms.Ps256:
            algorithm = 'Ps256 (RSASSA-PSS w/ SHA-256)'
        print("\tCOSE Algorithm:", algorithm)

# Get the COSE signed payload
payload = decoded.payload

print("\nA COSE signed messages contains 'claims' protected/signed by the CBOR Web Token in this case what is certified valid by a EU Member State. The CBOR-encoded claims payload is:") 
hexDump(payload)

print("\nDecoding the CBOR-encoded COSE claims into a more readable JSON format:")
payload = cbor2.loads(payload)

claim_names = { 1 : "Issuer", 6: "Issued At", 4: "Expiration time", -260 : "Health claims" }
for k in payload:
  if k != -260:
    n = f'Claim {k} (unknown)'
    msg = ''
    if k in claim_names:
       n = claim_names[k]
    if k == 4 and datetime.today().timestamp() > payload[k]:
        msg = ' <span style="color: red ;">!!! This certificate is no more valid!!!</span>'
    if k == 6 and datetime.today().timestamp() < payload[k]:
        msg = ' <span style="color: red ;">!!! This certificate is not yet valid!!!</span>'
    if k == 6 or k == 4:
        payload[k] = datetime.utcfromtimestamp(payload[k]).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"\t{n:20}: {payload[k]}{msg}")
payload = payload[-260][1]
# Encoding is https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
# And many binary values are from https://github.com/ehn-dcc-development/ehn-dcc-valuesets
n = "Health payload JSON"
print(f"\t{n:20}: ")

print(json.dumps(payload, indent=4, sort_keys=True, ensure_ascii=False, default=json_serial).replace('<','&lt;'))

# Deeper parser
print("\n\nHealth Certificate")
print("Using the <a href='https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf'>EU JSON specification</a>.\n")
if 'nam' in payload:
    names = payload['nam']
    if 'fn' in names:
        print("Last name:", names['fn'])
    if 'gn' in names:
        print("First name:", names['gn'])
    if 'fnt' in names and 'gnt' in names:
        print("Name as in passport (ICAO 9303 transliteration):", names['fnt'].replace('<','&lt;') + '&lt;&lt;' + names['gnt'].replace('<','&lt;'))
if 'dob' in payload:
    print("Birth date:", payload['dob'])
if 'v' in payload:
    for vaccine in payload['v']:
        print("\nVaccine for", decode(disease, vaccine['tg']))
        print("\tVaccine name:", decode(vaccine_product, vaccine['mp']), 'by', decode(vaccine_manufacturer, vaccine['ma']))
        print("\tDose:", vaccine['dn'], "out of", vaccine['sd'], "taken on", vaccine['dt'], "in", country[vaccine['co']], 'by', vaccine['is'])
if 't' in payload:
    for test in payload['t']:
        print("\nTest for", decode(disease, test['tg']), '/', decode(test_type, test['tt']))
        if 'nm' in test:
            print("\tName:", test['nm'])
        if 'ma' in test:
            print("\tTest device:", test['ma'], '/', decode(test_manf, test['ma']))
        print("\tTest taken on:", test['sc'], 'by', test['tc'], 'in', decode(country, test['co']))
        print("\tTest result:", decode(test_result, test['tr']))
if 'r' in payload:
    for recovery in payload['r']:
        print("\nRecovery from", decode(disease, recovery['tg']))
        print("\tPositive test on", recovery['fr'])
        print("\tCertified by", recovery['is'], 'in', decode(country, recovery['co']))
        print("\tValid from", recovery['df'], 'to', recovery['du'])
