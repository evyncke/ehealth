#!/bin/sh
cd /home/evyncke/ehealth/ietf/
echo "Affiliation; Name; Volunteering time" > data/nomcom16.csv
./nomcom.py  | /usr/bin/sort -bf >> data/nomcom16.csv
TZ='UTC' date +'Generated on the %c UTC' >> data/nomcom16.csv
