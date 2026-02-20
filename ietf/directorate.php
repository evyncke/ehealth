<?php
# Copyright 2022-2026 Eric Vyncke, evyncke@cisco.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
# HTTP/2 push of CSS via header()
header('Link: </participants2.js>;rel=preload;as=script,</directorate.js>;rel=preload;as=script,</utils.js>;rel=preload;as=script,</dirmembers.js>;rel=preload;as=script,</meetings.js>;rel=preload;as=script') ;
?><!doctype html>
<html lang="en">
<head>
<title>IETF WG Participants</title>
<!-- Required meta tags -->
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Bootstrap CSS -->
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
<!--- get all IETF participants onsite + per country statistics + date of collection -->
<!-- TODO handle past IETF meetings -->
	<script type="text/javascript" src="participants2.js"></script>
	<script type="text/javascript" src="directorate.js"></script>
	<script type="text/javascript" src="dirmembers.js"></script>
	<script type="text/javascript" src="meetings.js"></script>
	<script type="text/javascript" src="utils.js"></script>
<?php
$ip = $_SERVER['REMOTE_ADDR'];
$ipv4only_message = (strpos($ip, ':') === false) ? '<p><mark>Humm you are interested in IETF work but only use the legacy IPv4 protocol?</mark></p>' : '' ;
$queryDirectorate = (isset($_REQUEST['directorate'])) ? $_REQUEST['directorate'] : '' ;
?>
<script type="text/javascript">

var lastMeeting = meetings['last']['number'] ;
var queryDirectorate = '<?=$queryDirectorate?>' ;
//
function onLoad() {

	var text = document.getElementById('registrationDate') ;
	text.innerHTML = registrationCollectionDate + ' (UTC)' ;
	text = document.getElementById('directoratesDate') ;
	text.innerHTML = directoratesCollectionDate + ' (UTC)' ;

	var datalist = document.getElementById('directorates') ;
	// TODO add some sorting on acronyms !
	for (let acronym in directorates) {
		directorate = directorates[acronym] ;
		var option = document.createElement("option");
		option.value = acronym ;
		option.text = directorate.name ;
		datalist.appendChild(option) ;
	}
	if (queryDirectorate != '') {
		document.getElementById('directorateInput').value = queryDirectorate ;
		onChange(document.getElementById('directorateInput')) ;
	}
	return ;
} // onLoad()

bluesheetsString = '' ; // Raw format of the bluesheets
participantsCount = 0 ; 
participantsOnSiteCount = 0 ; 
participantsRemoteCount = 0 ; 
participantsUnknownCount = 0 ;
participantsOnsiteNames = [] ;
participantsRemoteNames = [] ; 
participantsUnknownNames = [] ;

// Find a participants based on the datatracker ID
function findParticipantById(id, table) {
        if (table[id]) return true ;
        return false ;
}

function displayCategory(elemId, name, onsite, remote, unknown, total, onsiteNames = null, remoteNames = null, unknownNames = null) {
	var leaders = document.getElementById(elemId) ;
	leaders.innerHTML = '<p>Out of the ' + total + ' ' + name + ', there are:</p><ul>' +
		'<li><abbr title="' + onsiteNames + '">' + onsite + ' on site</abbr>;</li>' +
		'<li><abbr title="' + remoteNames + '">' + remote + ' remote</abbr>;</li>' +
		'<li><abbr title="' + unknownNames + '">' + unknown + ' not registered yet </abbr>(or <abbr title="no correlation was possible between registration and datatracker data (different writing of the first & last names)">not found</abbr>).</li>' +
		'</ul>' ;
	document.getElementById(elemId + 'Onsite').style.width = Math.round(100.0*onsite/total) + "%" ;
	document.getElementById(elemId + 'Onsite').innerHTML = Math.round(100.0*onsite/total) + "%" ;
	document.getElementById(elemId + 'Remote').style.width = Math.round(100.0*remote/total) + "%" ;
	document.getElementById(elemId + 'Remote').innerHTML = Math.round(100.0*remote/total) + "%" ;
} ; 

function checkDirectorateMembers(directorateName, elem) {
	elem.insertAdjacentHTML('beforeend', '<p><em>Checking the status of chairs, secretaries, reviewers, and AD...</em></p>') ;
	var msg = '<ul>' ;
	for (let p in directorateMembers) {
        var roles = []
		for (let role in directorateMembers[p].role) {
			var directorateRole = directorateMembers[p].role[role].split('-') ;
			if (directorateRole[0] != directorateName)
				continue ;
            roles.push(directorateRole[1]) ;
		}
        if (roles != '') {
            msg += '<li>' + directorateMembers[p].name + ' (' + roles.join(', ') + '): ' ;
            if (findParticipantById(p, participantsOnsite) || findParticipantByName(directorateMembers[p].name, participantsOnsite) || findParticipantByName(directorateMembers[p].ascii_name, participantsOnsite))
                msg += '<b>onsite</b>;' ;
            else if (findParticipantById(p, participantsRemote) ||findParticipantByName(directorateMembers[p].name, participantsRemote) || findParticipantByName(directorateMembers[p].ascii_name, participantsRemote))
                msg += 'remote;' ;
            else
                msg += '<em>not found on registration</em>;' ;
            msg += '</li>' ;
}
    }
	msg += '</ul>' ;
	elem.insertAdjacentHTML('beforeend', msg) ;
}

function onChange(elem) {
	// Hide some previously displayed elements
	document.getElementById('participantsProgressBar').style.display = 'none' ;
	document.getElementById('participants').style.display = 'none' ;
	document.getElementById('resultText').innerHTML = '' ;
	// reset some values between runs
	participantsCount = 0 ; 
	participantsOnSiteCount = 0 ; 
	participantsRemoteCount = 0 ; 
	participantsUnknownCount = 0 ;
	participantsOnsiteNames = [] ;
	participantsRemoteNames = [] ; 
	participantsUnknownNames = [] ;
	// Check whether this is a valid WG
	if (! directorates[elem.value]) {
		console.log('Invalid name', elem.value) ;
		document.getElementById('resultText').insertAdjacentHTML('beforeend', '<p style="color: red;">Unknown directorate ' + elem.value + '.</p>') ;
		return ;
	}
	// Display progress to the user
	document.getElementById('resultText').insertAdjacentHTML('beforeend', '<h2>' + directorates[elem.value].name + ' WG<h2>') ;
	checkDirectorateMembers(elem.value, document.getElementById('resultText')) ;
}

</script>
<!-- Matomo -->
<script type="text/javascript">
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(["setDocumentTitle", document.domain + "/" + document.title]);
    _paq.push(["setCookieDomain", "*.ietf.vyncke.org"]);
    _paq.push(['trackPageView']);
      _paq.push(['enableLinkTracking']);
      (function() {
	          var u="//analytics.vyncke.org/";
		      _paq.push(['setTrackerUrl', u+'matomo.php']);
		      _paq.push(['setSiteId', '9']);
		          var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
		          g.type='text/javascript'; g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
			    })();
      </script>
<!-- End Matomo Code -->
</head>
<body onload="onLoad();">
<div class="container-fluid">
<h1>IETF Directorate Participations</h1>
<div class="row">
<div class="col">
Select an IETF Directorate:
<input list="directorates" id="directorateInput" onchange="onChange(this);">
<datalist id="directorates">
</datalist>
</div> <!-- col -->
</div> <!-- row -->
<div class="row">
<div id='resultText' class="col">
<p>Please select a directorate in the box above</p>
</div> <!-- resultText -->
<div id="participants"></div>
<div id="participantsProgressBar" class="progress" style="height: 20px; display: none;">
        <div id="participantsOnsite" class="progress-bar" style="width: 0%; background-color: green;"></div>
        <div id="participantsRemote" class="progress-bar" style="width: 0%; background-color: orange;"></div>
</div> <!-- ProgressBar -->

</div> <!-- row -->
<hr>
<?=$ipv4only_message?>
<p>
<em>Registration data collected on <span id="registrationDate"></span> (hourly refresh),  directorate as of <span id="directoratesDate"></span> (daily refresh),
 <a href="https://datatracker.ietf.org/api/">IETF data tracker</a> data.
The power of open data!</em><br/>
<small>Code is open source and stored on IPv4-only github <a href="https://github.com/evyncke/ehealth/tree/main/ietf">repo</a>.</small></p>
<!-- Matomo Image Tracker and warning about JS requirement -->
<noscript><img referrerpolicy="no-referrer-when-downgrade" src="https://analytics.vyncke.org/matomo.php?idsite=6&amp;rec=1" style="border:0" alt="" />
<b>This site requires javascript.</b></noscript>
<!-- End Matomo -->
</div><!-- container-fluid -->
<!-- Bootstrap bundle -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</body>
</html>