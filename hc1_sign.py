#!/usr/bin/env python3.8
import sys
import zlib
import argparse
import json
import cbor2
import ecdsa
from datetime import datetime
from base64 import b64encode, b64decode


from base45 import b45encode
from cose.algorithms import Es256
from cose.keys.curves import P256
from cose.algorithms import Es256, EdDSA
from cose.keys.keyparam import KpKty, KpAlg, EC2KpD, EC2KpX, EC2KpY, EC2KpCurve
from cose.headers import Algorithm, KID
from cose.keys import CoseKey
from cose.keys.keyparam import KpAlg, EC2KpD, EC2KpCurve
from cose.keys.keyparam import KpKty
from cose.keys.keytype import KtyEC2
from cose.messages import Sign1Message
import hashlib
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask

from ehealth_decode import hexDump

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
            return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


parser = argparse.ArgumentParser(description="Sign, B45 and compress a CBOR")

parser.add_argument(
    "--skip-signature", action="store_true", help="Skip the signature, make it dummy",
)

parser.add_argument(
    "-i",
    "--issuing-country",
    action="store",
    help="Issuing country, claim key 1, optional, ISO 3166-1 alpha-2 of issuer) (default is 'XX')",
    default="XX"
)
parser.add_argument(
    "-t",
    "--time-to-live",
    action="store",
    help="Time to live (for the expiration time, in seconds, default is 1 days)",
    default=1 * 24 * 3600
)
parser.add_argument(
    "-o",
    "--output",
    action="store",
    help="QR code filename"
)
parser.add_argument(
    "privkeyfile",
    default="ec-secp256k1-priv-key.pem",
    help="The private key to sign the request with; using <ec-secp256k1-priv-key.pem> as the default. PEM format.",
)
parser.add_argument(
    "pubkeyfile",
    default="ec-secp256k1-pub-key.pem",
    help="The associated public key; using <ec-secp256k1-pub-key.pem> as the default. PEM format.",
)

args = parser.parse_args()

payload = sys.stdin.buffer.read()

payload = json.loads(payload.decode("utf-8"))

# All the COSE claims

payload = {
           1: args.issuing_country,
           4: int(datetime.now().timestamp() - args.time_to_live),
           6: int(datetime.today().timestamp() - 2 * args.time_to_live),
           -260: {
                1: payload,
            },
}

print('The set of to-be-signed COSE claims is now:\n')
print(' * -260: health claims')
print(' * 1: issuer')
print(' * 4: expiration time')
print(' * 6: issued at') 
print('\nWhich can be displayed as the JSON object:')
print(json.dumps(payload, indent=4, sort_keys=True, ensure_ascii=False, default=json_serial).replace('<','&lt;'))

payload = cbor2.dumps(payload)

print('\nAfter CBOR compression/encoding, it is now:')
hexDump(payload)

if args.skip_signature:
    print("Using a dummy signature")

    # Build a dummy COSE
    # Tag 18
    # [b'\xa2\x01&\x04H\x00\x00\x00\x00\x00\x00\x00\x00', {}, payload, 64 bytes = signature ]
    # I.e., protected header, unprotected header, payload, signature
    out = cbor2.CBORTag(18, [ b'\xa2\x01&\x04H\x00\x00\x00\x00\x00\x00\x00\x00',
        {},
        payload,
        b'DummySignature!!DummySignature!!DummySignature!!DummySignature!!'])
    out = cbor2.dumps(out)
else:
    print("Signing the content")
    # Note - we only need the public key for the KeyID calculation - we're not actually using it.
    # Recent version uses the hash of the certificate, so, simply using a dummy key id of all 0
    keyid = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    # Read in the private key that we use to actually sign this
    #
    with open(args.privkeyfile, "rb") as file:
        pem = file.read()
    privkey_pem = load_pem_private_key(pem, password=None)
    priv = privkey_pem.private_numbers().private_value.to_bytes(32, byteorder="big")

    # Prepare a message to sign; specifying algorithm and keyid
    # that we (will) use
    #
    msg = Sign1Message(phdr={Algorithm: Es256, KID: keyid}, payload=payload)
    print('\nCOSE sign1 message with algorithm & key id:')
    print(msg)

    # Create the signing key - use ecdsa-with-SHA256
    # and NIST P256 / secp256r1
    #
    cose_key = {
        KpKty: KtyEC2,
        KpAlg: Es256,  # ecdsa-with-SHA256
        EC2KpCurve: P256,  # Ought to be pk.curve - but the two libs clash
        EC2KpD: priv,
    }

    # Encode the message (which includes signing)
    #
    msg.key = CoseKey.from_dict(cose_key)
    out = msg.encode()

print('\nAfter COSE signature and CBOR encoding:')
hexDump(out, 'orange', offset = 20, length = len(payload))

# Compress with ZLIB
#
before_length = len(out)
out = zlib.compress(out, 9)
after_length = len(out)
if before_length <= after_length:
    print("\nMessage is now compressed with ZLIB but the compression was not really useful as it increased the size from",before_length,"to",after_length,"bytes")
else:
    print("\nMessage is now compressed with ZLIB and the compression was useful as it decreased the size from",before_length,"to",after_length,"bytes")
hexDump(out)

# And base45 encode the result
#
out = b'HC1:' + b45encode(out).encode('ascii')

# sys.stdout.buffer.write(out)
print('\nPrepending "HC1:" and base45 encoding:\n', out)

# Create a QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
    box_size=4,
    border=4)
qr.add_data(out)
qr.make(fit=True)

#img = qr.make_image(image_factory=StyledPilImage, embeded_image_path="fake.png", color_mask=SolidFillColorMask(back_color = (255,255,255), front_color = (255,0,0)))
img = qr.make_image(image_factory=StyledPilImage, embeded_image_path="/home/evyncke/ehealth/fake.png", color_mask=SolidFillColorMask(back_color = (255,100,100), front_color = (0,0,0)))
if not args.output:
    img.save('generated.png')
else:
    img.save(args.output)
