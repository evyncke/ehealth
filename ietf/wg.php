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
header('Link: </participants2.js>;rel=preload;as=script,</wg.js>;rel=preload;as=script,</utils.js>;rel=preload;as=script,</wgchairs.js>;rel=preload;as=script,</meetings.js>;rel=preload;as=script') ;
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
	<script type="text/javascript" src="participants2.js"></script>
	<script type="text/javascript" src="wg.js"></script>
	<script type="text/javascript" src="wgchairs.js"></script>
	<script type="text/javascript" src="meetings.js"></script>
	<script type="text/javascript" src="utils.js"></script>
<?php
$ip = $_SERVER['REMOTE_ADDR'];
$ipv4only_message = (strpos($ip, ':') === false) ? '<p><mark>Humm you are interested in IETF work but only use the legacy IPv4 protocol?</mark></p>' : '' ;
$queryWG = (isset($_REQUEST['wg'])) ? $_REQUEST['wg'] : '' ;
?>
<script type="text/javascript">

var lastMeeting = meetings['last']['number'] ;
var queryWG = '<?=$queryWG?>' ;
//
function onLoad() {

	var text = document.getElementById('registrationDate') ;
	text.innerHTML = registrationCollectionDate + ' (UTC)' ;
	text = document.getElementById('wgsDate') ;
	text.innerHTML = wgsCollectionDate + ' (UTC)' ;

	var datalist = document.getElementById('wgs') ;
	// TODO add some sorting on acronyms !
	for (let acronym in wgs) {
		wg = wgs[acronym] ;
		if (! wg.meeting) continue ;
		var option = document.createElement("option");
		option.value = acronym ;
		option.text = wg.name ;
		datalist.appendChild(option) ;
	}
	if (queryWG != '') {
		document.getElementById('wgInput').value = queryWG ;
		onChange(document.getElementById('wgInput')) ;
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

function analyseLine(value, index) {
	if (index < 6) return ; // Skip the first lines
	if (value == '') return ; // Somes times empty lines...
	var name = value.split("\t")[0] ;
	participantsCount ++ ;
	if (findParticipantByName(name, participantsOnsite)) {
		console.log(name, "is on site") ;
		participantsOnSiteCount++ ;
		participantsOnsiteNames.push(name) ;
	} else if (findParticipantByName(name, participantsRemote)) {
		console.log(name, "is remote") ;
		participantsRemoteCount++ ;
		participantsRemoteNames.push(name) ;
	} else {
		participantsUnknownCount++ ;
		participantsUnknownNames.push(name) ;
		fuzzyMatch(name) ;
	}
}

function analyseBluesheets() {
  document.getElementById('resultText').innerHTML += '<p><em>Analysing the blue sheets....</em></p>' ;
  var lines = bluesheetsString.split("\n") ;
  lines.forEach(analyseLine) ;
  // Now let's display the outcome
  document.getElementById('participants').style.display = 'block' ;
  displayCategory('participants', 'expected attendees', participantsOnSiteCount, participantsRemoteCount, participantsUnknownCount, participantsCount,
		participantsOnsiteNames.join(', '), participantsRemoteNames.join(', '), participantsUnknownNames.join(', '))
  document.getElementById('participantsProgressBar').style.display = 'flex' ;
}

function checkWGLeaders(wgName, elem) {
	elem.insertAdjacentHTML('beforeend', '<p><em>Checking the status of chairs and delegates...</em></p>') ;
	var msg = '<ul>' ;
	for (let p in wgChairs) {
		for (let role in wgChairs[p].role) {
			var wgRole = wgChairs[p].role[role].split('-') ;
			if (wgRole[0] != wgName)
				continue ;
			msg += '<li>' + wgChairs[p].name + ' (' + wgRole[1] + '): ' ;
			if (findParticipantByName(wgChairs[p].name, participantsOnsite) || findParticipantByName(wgChairs[p].ascii_name, participantsOnsite))
				msg += 'onsite;' ;
			else if (findParticipantByName(wgChairs[p].name, participantsRemote) || findParticipantByName(wgChairs[p].ascii_name, participantsRemote))
				msg += 'remote;' ;
			else
				msg += 'not found on registration;' ;
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
	if (! wgs[elem.value]) {
		console.log('Invalid name', elem.value) ;
		document.getElementById('resultText').insertAdjacentHTML('beforeend', '<p style="color: red;">Unknown or not meeting WG/BoF ' + elem.value + '.</p>') ;
		return ;
	}
	// Display progress to the user
	document.getElementById('resultText').insertAdjacentHTML('beforeend', '<h2>' + wgs[elem.value].name + ' WG<h2>') ;
	checkWGLeaders(elem.value, document.getElementById('resultText')) ;
	var bluesheetsFilename = wgs[elem.value].bluesheets ;
	if (! bluesheetsFilename) {
		console.log('No bluesheets') ;
		document.getElementById('resultText').insertAdjacentHTML('beforeend', '<p style="color: red;">Alas, no blue sheets are available for the previous WG meeting...</p>') ;
		return ;
	}
	var uri = "/proceedings/" + lastMeeting + "/bluesheets/" + bluesheetsFilename ;
	var proxiedUri = "dt_proxy.php?url=" + encodeURIComponent(uri) ;
	document.getElementById('resultText').insertAdjacentHTML('beforeend', '<p><em>Fetching <a href="https://www.ietf.org' + uri + '">blue sheets</a> of the last WG meeting.</em></p>') ;
	var response = fetch(proxiedUri) // fetch() returns a 'Promise' object
	        // Could use .catch(error =>) to handle errors
		.then(response => response.text()) // now we have a 'Response' object
		.then(data => {
		          bluesheetsString = data ;
			  analyseBluesheets() ;
			}) ;
}

</script>
<!-- Matomo -->
<script type="text/javascript">
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(["setDocumentTitle", document.domain + "/" + document.title]);
    _paq.push(["setCookieDomain", "*.ehealth.vyncke.org"]);
    _paq.push(['trackPageView']);
      _paq.push(['enableLinkTracking']);
      (function() {
	          var u="//analytics.vyncke.org/";
		      _paq.push(['setTrackerUrl', u+'matomo.php']);
		      _paq.push(['setSiteId', '6']);
		          var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
		          g.type='text/javascript'; g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
			    })();
      </script>
<!-- End Matomo Code -->
</head>
<body onload="onLoad();">
<div class="container-fluid">
<h1>IETF WG Participations</h1>
<div class="row">
<div class="col">
Select an IETF Working Group:
<input list="wgs" id="wgInput" onchange="onChange(this);">
<datalist id="wgs">
</datalist>
</div> <!-- col -->
</div> <!-- row -->
<div class="row">
<div id='resultText' class="col">
<p>Please select a WG in the box above</p>
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
<em>Registration data collected on <span id="registrationDate"></span> (hourly refresh),  WG/BoF as of <span id="wgsDate"></span> (daily refresh),
 <a href="https://datatracker.ietf.org/api/">IETF data tracker</a> data.
The power of open data!</em><br/>
<small>Code is open source and store on IPv4-only github <a href="https://github.com/evyncke/ehealth/tree/main/ietf">repo</a>.</small></p>
<!-- Matomo Image Tracker and warning about JS requirement -->
<noscript><img referrerpolicy="no-referrer-when-downgrade" src="https://analytics.vyncke.org/matomo.php?idsite=6&amp;rec=1" style="border:0" alt="" />
<b>This site requires javascript.</b></noscript>
<!-- End Matomo -->
</div><!-- container-fluid -->
<!-- Bootstrap bundle -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</body>
</html>