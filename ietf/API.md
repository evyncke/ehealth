# Getting the next IETF meeting

https://datatracker.ietf.org/api/v1/meeting/meeting/?type=ietf&offset=0&limit=1

<number>113</number>
<schedule>/api/v1/meeting/schedule/1862/</schedule>
<type>/api/v1/name/meetingtypename/ietf/</type>
<country>AT</country>
<resource_uri>/api/v1/meeting/meeting/1532/</resource_uri>
<id type="integer">1532</id>

## Meeting URI
https://datatracker.ietf.org/api/v1/meeting/meeting/1532/

To display the very same information.

## Schedule
https://datatracker.ietf.org/api/v1/meeting/schedule/1862/

Display nothing interesting :-(

## Session
https://datatracker.ietf.org/api/v1/meeting/session/ 
or
https://datatracker.ietf.org/api/v1/meeting/session/?meeting=1532&type=regular

<group>/api/v1/group/group/1479/</group>
<assignments type="list">
<value>/api/v1/meeting/schedtimesessassignment/1/</value>
</assignments>
<meeting>/api/v1/meeting/meeting/65/</meeting>
<type>/api/v1/name/timeslottypename/regular/</type>


## Bluesheets
https://datatracker.ietf.org/api/v1/doc/document/?group=1958&type=bluesheets&offset=0
Last one is .txt

or rather https://datatracker.ietf.org/api/v1/doc/document/?group=1958&type=bluesheets&time__gte=2021-11-01T00:00:00
to return only one..

<group>/api/v1/group/group/1958/</group>
<name>bluesheets-112-dprive-202111111200</name>
<resource_uri>/api/v1/doc/document/bluesheets-112-dprive-202111111200/</resource_uri>
<time>2021-11-11T07:38:55</time>
<title>Bluesheets IETF112: dprive : Thu 12:00</title>
<type>/api/v1/name/doctypename/bluesheets/</type>
<uploaded_filename>bluesheets-112-dprive-202111111200-00.txt</uploaded_filename>

Then use https://www.ietf.org/proceedings/112/bluesheets/ + uploaded filename
first_name <spc> last_name <tab> affiliation <crlf>
