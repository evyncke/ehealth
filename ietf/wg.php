<?php
# Copyright 2022 Eric Vyncke, evyncke@cisco.com
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
header('Link: </ietf/participants.js>;rel=preload;as=script,</ietf/wg.js>;rel=preload;as=script') ;
?><!doctype html>
<html lang="en">
<head>
<title>IETF Participants and COVID-19</title>
<!-- Required meta tags -->
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Bootstrap CSS -->
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
<!--- get all IETF participants onsite + per country statistics + date of collection -->
	<script type="text/javascript" src="participants.js"></script>
	<script type="text/javascript" src="wg.js"></script>
<?php
$ip = $_SERVER['REMOTE_ADDR'];
$ipv4only_message = (strpos($ip, ':') === false) ? '<p><mark>Humm you are interested in IETF work but only use the legacy IPv4 protocol?</mark></p>' : '' ;
?>
<script type="text/javascript">

shortNames = new Map([['Antoni', 'Tony'], ['Anthony', 'Tony'], ['Frederick', 'Fred'], ['James', 'Jim'], ['Timothy','Tim'],
	['Michael', 'Mike'], ['Mickael', 'Mike'], ['Stephen', 'Steve'], ['Stephan', 'Steve'], ['Steven', 'Steve'], ['Robert', 'Bob'],
	['Nicolas', 'Nick'], ['Nicholas', 'Nick'], ['Nicklas', 'Nick'], ['Wesley', 'Wes'],
	['Edward', 'Ted'], ['Patrick', 'Pat'], ['Patrik', 'Pat'],['Deborah', 'Deb'], ['Benjamin', 'Ben'],
	['Louis', 'Lou'], ['Godred', 'Gorry'], ['Russell', 'Russ'], ['Lester', 'Les'],
	['André', 'Andre'], ['Luc André', 'Luc Andre'],
	['Göran', 'Goeran'], ['Hernâni', 'Hernani'], ['Frédéric', 'Frederic'],
	['Olorunlob', 'Loba'], ['Bradford', 'Brad'],
	['Geoffrey', 'Geoff'], ['Balázs', 'Balazs'], ['János', 'Janos'],
	['Alexandre', 'Alex'], ['Alexander', 'Alex'],['Gregory', 'Greg'],['Gregory', 'Greg'],
	['Christopher', 'Chris'], ['Christophe', 'Chris'], ['Samuel', 'Sam'], ['Richard', 'Dick'],
	['Thomas', 'Tom'], ['David', 'Dave'], ['Bernard', 'Bernie'], ['Peter', 'Pete'], ['Donald', 'Don']]) ;
// Find a participants based on "first last" in the participants table containing lastname firstname
function findParticipant(fullName, table) {
	if (! fullName) return false ;
	// Exceptions
	if (fullName == 'Ines Robles') fullName = 'Maria Ines Robles' ;
	if (fullName == 'Spencer Dawkins') fullName = 'Paul Spencer Dawkins' ;
	if (fullName == 'Jose Ignacio Alvarez-Hamelin') fullName = 'J. Ignacio Alvarez-Hamelin' ;
	// Some names out of Datatrack have a middle initial, which is not used in the registration
	var tokens = fullName.split(' ') ;
	if (shortNames.get(tokens[0])) tokens[0] = shortNames.get(tokens[0]) ;
	var fullName2 = tokens[0] + ' ' + tokens[tokens.length-1] ;
	fullName = fullName.toUpperCase() ;
	fullName2 = fullName2.toUpperCase() ;
	for (let i = 0; i < table.length; i++) {
		if (shortNames.get(table[i][1])) table[i][1] = shortNames.get(table[i][1]) ;
		var participantName = table[i][1] + ' ' + table[i][0] ;
		participantName = participantName.toUpperCase() ;
		if (fullName == participantName) return true ;
		if (fullName2 == participantName) return true ;
	}
	return false ;
}

function fuzzyMatch(fullName) {
	console.log('Not found by exact match: ' + fullName) ;
	if (! fullName) return ;
	// participantsOnsite
//	var table = participantsOnsite ;
	var table = participantsRemote ;
	var tokens = fullName.split(' ') ;
	var lastName = tokens[tokens.length-1].toUpperCase() ;
	for (let i = 0; i < table.length ; i++) {
		if (lastName == table[i][0].toUpperCase()) 
			console.log('  Fuzzy match with ' + table[i][1] + ' / ' + table[i][0]) ;
	}
}

//
function onLoad() {

	var text = document.getElementById('registrationDate') ;
	text.innerHTML = registrationCollectionDate + ' (UTC)' ;

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

	return ;
} // onLoad()


function onChange(elem) {
	console.log("onChange, elem:", elem.value) ;
	document.getElementById('resultText').innerHTML = '<h2>' + wgs[elem.value].name + ' WG<h2>' ;
	var bluesheetsFilename = wgs[elem.value].bluesheets ;
	console.log('filename', bluesheetsFilename) ;
	if (! bluesheetsFilename) {
		console.log('No bluesheets') ;
		document.getElementById('resultText').innerHTML += '<p style="color: red;">Alas, no blue sheets are available for the previous WG meeting...</p>' ;
		return ;
	}
	var uri = "https://www.ietf.org/proceedings/112/bluesheets/" + bluesheetsFilename ;
	document.getElementById('resultText').innerHTML += '<p><em>Fetching <a href="' + uri + '">blue sheets</a> of the latest WG meeting.</em></p>' ;
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
<div class="col-sm-12 col-lg-6 col-xxl-4">
Select an IETF Working Group:
<input list="wgs" id="wgInput" onchange="onChange(this);">
<datalist id="wgs">
</datalist>
</div> <!-- col -->
<div id='resultText'>
<p>Please select a WG in the box above</p>
</div>
</div> <!-- row -->
<hr>
<?=$ipv4only_message?>
<p>If you want to know more on how IETF technologies are used worldwide for "COVID-19 certificates", here are a <a href="https://ehealth.vyncke.org">decoder and explanations</a>.<br/>
<em>Registration data collected on <span id="registrationDate"></span> (hourly refresh), <a href="https://datatracker.ietf.org/api/">IETF data tracker</a> data, and <a href="https://ourworldindata.org/">https://ourworldindata.org/</a>, itself based on <a href="https://github.com/CSSEGISandData/COVID-19">JHU CSSE COVID-19 Data</a>.
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
