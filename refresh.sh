#!/bin/bash -e
./update-rat.sh > test-manf.json
wget --timestamp https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/main/country-2-codes.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/raw/main/disease-agent-targeted.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/raw/main/test-result.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/raw/main/test-type.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/raw/main/vaccine-mah-manf.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/raw/main/vaccine-medicinal-product.json
wget --timestamp https://github.com/ehn-dcc-development/ehn-dcc-valuesets/blob/main/vaccine-prophylaxis.json
