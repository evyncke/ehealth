#!/bin/sh
cd /home/evyncke/ehealth/ietf/
echo "Affiliation; Name; Volunteering time" > data/nomcom17.csv
./nomcom.py  | /usr/bin/sort -bf >> data/nomcom17.csv
TZ='UTC' date +'Generated on the %c UTC' >> data/nomcom17.csv
