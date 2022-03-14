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
header('Link: </ietf/draftauthors.js>;rel=preload;as=script,</ietf/participants.js>;rel=preload;as=script,</ietf/wgchairs.js>;rel=preload;as=script,</ietf/leaders.js>;rel=preload;as=script,</ietf/owid.png>;rel=preload;as=image,</ietf/isoCountry.js>;rel=preload;as=script,</ietf/wg.js>;rel=preload;as=script') ;
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
	<script type="text/javascript" src="leaders.js"></script>
	<script type="text/javascript" src="wgchairs.js"></script>
	<script type="text/javascript" src="wg.js"></script>
	<script type="text/javascript" src="draftauthors.js"></script>
	<script type="text/javascript" src="isoCountry.js"></script>
<!--- Google charts -->
	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<?php
require_once('/var/www/vendor/autoload.php') ;
use GeoIp2\Database\Reader;
$reader = new Reader('/var/www/matomo/misc/DBIP-City.mmdb') ;
$ip = $_SERVER['REMOTE_ADDR'];
$ipv4only_message = (strpos($ip, ':') === false) ? '<p><mark>Humm you are interested in IETF work but only use the legacy IPv4 protocol?</mark></p>' : '' ;
$mycountry = $reader->city($ip) ;
$mycountry = $mycountry->country->isoCode ;
?>
<script type="text/javascript">
myCountry = countryISOMapping['<?=$mycountry?>'] ;
ietfCountry = 'AUT' ;
covid_data = '' ;

function loadCovidData() {
response = fetch('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.json') // fetch() returns a 'Promise' object
	// Could use .catch(error =>) to handle errors
	.then(response => response.json()) // now we have a 'Response' object
	.then(data => {
		covid_data = data ;
		drawChart()
		});
}

// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(loadCovidData);

shortNames = new Map([['Antoni', 'Tony'], ['Anthony', 'Tony'], ['Frederick', 'Fred'], ['James', 'Jim'], ['Timothy','Tim'],
	['Michael', 'Mike'], ['Mickael', 'Mike'], ['Stephen', 'Steve'], ['Stephan', 'Steve'], ['Steven', 'Steve'], ['Robert', 'Bob'],
	['Nicolas', 'Nick'], ['Nicholas', 'Nick'], ['Nicklas', 'Nick'], ['Wesley', 'Wes'],
	['Edward', 'Ted'], ['Patrick', 'Pat'], ['Patrik', 'Pat'],['Deborah', 'Deb'], ['Benjamin', 'Ben'],
	['Louis', 'Lou'], ['Godred', 'Gorry'], ['Russell', 'Russ'], ['Lester', 'Les'],
	['André', 'Andre'], ['Luc André', 'Luc Andre'],['Matthew', 'Mat'],
	['Göran', 'Goeran'], ['Hernâni', 'Hernani'], ['Frédéric', 'Frederic'],
	['Olorunlob', 'Loba'], ['Bradford', 'Brad'],['Gábor', 'Gabor'],
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

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawChart() {
	var data = new google.visualization.DataTable();
	data.addColumn('string', 'Country');
	data.addColumn('number', 'Onsite Participants');
	data.addColumn({type : 'string', role : 'tooltip'}) ;
	// Add data
	var participantsCount = 0 ;
	var weightedNewCases = 0.0 ;
	var minCountry = '', maxCountry = '', minNewcases = 9999999, maxNewcases = -1 ;
	var largeCountries = new Array(myCountry, ietfCountry) ;
	for (let country in countries) {
		participants = countries[country] ;
		participantsCount += participants ;
		isoCode = countryISOMapping[country] ;
		if (participants > 5)
			largeCountries.push(isoCode) ;
		newCases = covid_data[isoCode].new_cases_smoothed_per_million ;
		weightedNewCases += participants * newCases ;
		if (newCases < minNewcases) {
			minNewcases = newCases;
			minCountry = isoCode ;
		}
		if (newCases > maxNewcases) {
			maxNewcases = newCases;
			maxCountry = isoCode ;
		}
		data.addRow([isoCode, participants, isoCode + ' (' + covid_data[isoCode].location + '), ' + participants + ' participants, new cases: ' + newCases + '/million']) ;
	}
	// Sort the data based on the onsite participants
	data.sort({column: 1, desc: true}) ;
	// Set chart options
	var options = {'title':'Onsite participants per country',
		sliceVisibilityThreshold: .01,
		'width':500,
		'height':500};
	
	// Instantiate and draw our chart, passing in some options.
	var chart = new google.visualization.PieChart(document.getElementById('pie_chart_div'));
	chart.draw(data, options);

	var text = document.getElementById('data') ;
	weightedNewCases /= participantsCount ;
	owidUrl = 'https://ourworldindata.org/explorers/coronavirus-data-explorer?zoomToSelection=true&time=2021-06-16..latest&facet=none&pickerSort=desc&pickerMetric=new_cases_per_million&Metric=Confirmed+cases&Interval=7-day+rolling+average&Relative+to+Population=true&Color+by+test+positivity=false&country=' + largeCountries.join('~') ;
	text.innerHTML = "<p>There are " + participantsCount + " in person participants. 7-day-smoothed new cases per million:<ul>" +
		"<li>weighted on all participants: " + Math.round(weightedNewCases) + "</li>" +
		"<li>country with minimum new cases: " + minCountry + " (" + covid_data[minCountry].location + ") with " + minNewcases + "</li>" +
		"<li>country with maximum new cases: " + maxCountry + " (" + covid_data[maxCountry].location + ") with " + Math.round(maxNewcases) + "</li>" +
		"<li>your country (based on your IP address): " + myCountry + " (" + covid_data[myCountry].location + ") with  " + Math.round(covid_data[myCountry].new_cases_smoothed_per_million) + "</li>" +
		"<li>IETF venue country: " + ietfCountry + " (" + covid_data[ietfCountry].location + ") with " + Math.round(covid_data[ietfCountry].new_cases_smoothed_per_million) + "</li>" +
		"</ul></p>" +
		"<p>Our world of data has a nice historical graphic for the new cases for all countries with more than 5 IETF participants: <a href='" + owidUrl +
		"' target='_window'>here</a><span class='glyphicon glyphicon-new-window'></span>.</p><div class='text-center'><a href='" + owidUrl + "' target='_window'><img src='owid.png' class='img-fluid rounded' width='50%' height='auto'/></a></div>"
	text = document.getElementById('registrationDate') ;
	text.innerHTML = registrationCollectionDate + ' (UTC)' ;
	text = document.getElementById('wgChairsDate') ;
	text.innerHTML = wgChairsCollectionDate + ' (UTC)' ;
	text = document.getElementById('draftAuthorsDate') ;
	text.innerHTML = draftAuthorsCollectionDate + ' (UTC)' ;
}

function displayCategory(elemId, name, onsite, remote, unknown, total) {
	leaders = document.getElementById(elemId) ;
	leaders.innerHTML = '<p>Out of the ' + total + ' ' + name + ', there are:</p><ul>' +
		'<li>' + onsite + ' on site;</li>' +
		'<li>' + remote + ' remote;</li>' +
		'<li>' + unknown + ' not registered yet (or <abbr title="no correlation was possible between registration and datatracker data (different writing of the first & last names)">not found</abbr>).</li>' +
		'</ul>' ;
	document.getElementById(elemId + 'Onsite').style.width = Math.round(100.0*onsite/total) + "%" ;
	document.getElementById(elemId + 'Onsite').innerHTML = Math.round(100.0*onsite/total) + "%" ;
	document.getElementById(elemId + 'Remote').style.width = Math.round(100.0*remote/total) + "%" ;
	document.getElementById(elemId + 'Remote').innerHTML = Math.round(100.0*remote/total) + "%" ;
}
//
function onLoad() {
	// Let's work on the I* leadership presence
	leadersOnsite = 0 ;
	leadersRemote = 0 ;
	leadersUnknown = 0 ;
	leadersTotal = 0 ;
	for (let id in leaders) {
		leader = leaders[id] ;
		if (findParticipant(leader.name, participantsOnsite))
			leadersOnsite++ ;
		else if (findParticipant(leader.ascii, participantsOnsite))
			leadersOnsite++ ;
		else if (findParticipant(leader.name, participantsRemote))
			leadersRemote++ ;
		else if (findParticipant(leader.ascii, participantsRemote))
			leadersRemote++ ;
		else {
			leadersUnknown++ ;
			fuzzyMatch(leader.name) ;
		}
		leadersTotal ++ ;
	}
	displayCategory('leaders', 'IESG/IAB members', leadersOnsite, leadersRemote, leadersUnknown, leadersTotal) ;

	// get the list of all WG
	wgChairsOnsiteList = []
	wgChairsRemoteList = []
	for (let wg in wgs) {
		wgChairsOnsiteList[wg] = 0 ;
		wgChairsRemoteList[wg] = 0 ;
	}

	// Let's work on the WG chairs presence
	wgChairsOnsite = 0 ;
	wgChairsRemote = 0 ;
	wgChairsUnknown = 0 ;
	wgChairsTotal = 0 ;
	for (let id in wgChairs) {
		leader = wgChairs[id] ;
		if (findParticipant(leader.name, participantsOnsite)) {
			wgChairsOnsite++ ;
			for (let role in leader['role']) {
				if (leader['role'][role].endsWith('-chair')) wgName = leader['role'][role].slice(0, -6) ; // remove the trailing "-chair"
				else if (leader['role'][role].endsWith('-delegate')) wgName = leader['role'][role].slice(0, -9) ; // remove the trailing "-delegate"
				wgChairsOnsiteList[wgName]++ ;
			}
		} else if (findParticipant(leader.ascii, participantsOnsite)){
			wgChairsOnsite++ ;
			for (let role in leader['role']) {
				if (leader['role'][role].endsWith('-chair')) wgName = leader['role'][role].slice(0, -6) ; // remove the trailing "-chair"
				else if (leader['role'][role].endsWith('-delegate')) wgName = leader['role'][role].slice(0, -9) ; // remove the trailing "-delegate"
				wgChairsOnsiteList[wgName]++ ;
			}
		} else if (findParticipant(leader.name, participantsRemote)){
			wgChairsRemote++ ;
			for (let role in leader['role']) {
				if (leader['role'][role].endsWith('-chair')) wgName = leader['role'][role].slice(0, -6) ; // remove the trailing "-chair"
				else if (leader['role'][role].endsWith('-delegate')) wgName = leader['role'][role].slice(0, -9) ; // remove the trailing "-delegate"
				wgChairsRemoteList[wgName]++ ;
			}
		} else if (findParticipant(leader.ascii, participantsRemote)){
			wgChairsRemote++ ;
			for (let role in leader['role']) {
				if (leader['role'][role].endsWith('-chair')) wgName = leader['role'][role].slice(0, -6) ; // remove the trailing "-chair"
				else if (leader['role'][role].endsWith('-delegate')) wgName = leader['role'][role].slice(0, -9) ; // remove the trailing "-delegate"
				wgChairsRemoteList[wgName]++ ;
			}
		} else {
			fuzzyMatch(leader.name) ;
			wgChairsUnknown++ ;
		}
		wgChairsTotal ++ ;
	}
	displayCategory('wg_chairs', 'WG chairs or delegates', wgChairsOnsite, wgChairsRemote, wgChairsUnknown, wgChairsTotal) ;
	onSiteWG = [] ;
	onSiteRemoteWG = [] ;
	nobodyWG = [] ;
	for (let wg in wgChairsOnsiteList) {
		if (wgs[wg].meeting)
			wgHTML = '<b>' + wg + '</b>' 
		else
			wgHTML = '<i>' + wg + '</i>' ;
		if (wgChairsOnsiteList[wg] > 0) onSiteWG.push(wgHTML) 
		else if (wgChairsRemoteList[wg] > 0) onSiteRemoteWG.push(wgHTML) ;
		else nobodyWG.push(wgHTML) ;
	}
	document.getElementById('onsite_chairs_text').innerHTML = onSiteWG.sort().join(', ') ;
	document.getElementById('remote_chairs_text').innerHTML = onSiteRemoteWG.sort().join(', ')  ;
	document.getElementById('no_chairs_text').innerHTML = nobodyWG.sort().join(', ') ;


	// Let's work on the WG chairs presence
	draftAuthorsOnsite = 0 ;
	draftAuthorsRemote = 0 ;
	draftAuthorsUnknown = 0 ;
	draftAuthorsTotal = 0 ;
	for (let id in draftAuthors) {
		author = draftAuthors[id] ;
		if (findParticipant(author.name, participantsOnsite))
			draftAuthorsOnsite++ ;
		else if (findParticipant(author.name, participantsRemote))
			draftAuthorsRemote++ ;
		else {
//			fuzzyMatch(author.name) ;
			draftAuthorsUnknown++ ;
		}
		draftAuthorsTotal ++ ;
	}
	displayCategory('draft_authors', 'draft authors in the last 4 months', draftAuthorsOnsite, draftAuthorsRemote, draftAuthorsUnknown, draftAuthorsTotal) ;
} // onLoad()

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
<h1>IETF Participants and COVID-19</h1>
<div class="row">
<div class="col-sm-12 col-lg-6 col-xxl-4">
<h2>On-site participants</h2>
<div id="pie_chart_div">Please wait while loading... if not loaded after 1 minute, please reload</div>
<p>Hoover over one pie piece to get more information.</p>
</div> <!-- col -->

<div class="col-sm-12 col-lg-6 col-xxl-4">
<h2>COVID-19 Data</h2>
<div id="data"></div>
</div> <!-- col -->

<div class="col-sm-12 col-lg-6 col-xxl-4">
<h2>I* Participation</h2>
<div id="leaders">Please wait while consolidating the data...</div>
<div id="leadersProgressBar" class="progress" style="height: 20px;">
	<div id="leadersOnsite" class="progress-bar" style="width: 0%; background-color: green;"></div>
	<div id="leadersRemote" class="progress-bar" style="width: 0%; background-color: orange;"></div>
</div> <!-- leadersProgressBar -->

<hr>

<h2>Working Groups Chairs Participation</h2>
<div id="wg_chairs">Please wait while consolidating the data...</div>

<button class="btn btn-outline-info btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#onsite_chairs">WG with at least one chair or delegate on site</button>
<div id="onsite_chairs" class="collapse">
	<div class="card card-body">
		<span id="onsite_chairs_text"></span>
	</div> <!-- card -->
</div> <!-- collapse -->
<br>
<button class="btn btn-outline-info btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#remote_chairs">WG with at least one chair or delegate remote but none on site</button>
<div id="remote_chairs" class="collapse">
	<div class="card card-body">
		<span id="remote_chairs_text"></span>
	</div> <!-- card -->
</div> <!-- collapse -->
<br>
<button class="btn btn-outline-info btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#no_chairs">WG with no registered chairs / delegates</button>
<div id="no_chairs" class="collapse">
	<div class="card card-body">
		<span id="no_chairs_text"></span>
	</div> <!-- card -->
</div> <!-- collapse -->

<br>
<a href="wg.php">More information per working group.</a>
<br>

<div id="wg_chairsProgressBar" class="progress" style="height: 20px;">
	<div id="wg_chairsOnsite" class="progress-bar" style="width: 0%; background-color: green;"></div>
	<div id="wg_chairsRemote" class="progress-bar" style="width: 0%; background-color: orange;"></div>
</div> <!-- wg_chairsProgressBar -->

<hr>

<h2>Recent Draft Authors Participation</h2>
<div id="draft_authors">Please wait while consolidating the data...</div>
<div id="draft_authorsProgressBar" class="progress" style="height: 20px;">
	<div id="draft_authorsOnsite" class="progress-bar" style="width: 0%; background-color: green;"></div>
	<div id="draft_authorsRemote" class="progress-bar" style="width: 0%; background-color: orange;"></div>
</div> <!-- wg_chairsProgressBar -->

</div> <!-- col -->

</div> <!-- row -->
<hr>
<?=$ipv4only_message?>
<p>If you want to know more on how IETF technologies are used worldwide for "COVID-19 certificates", here are a <a href="https://ehealth.vyncke.org">decoder and explanations</a>.<br/>
<em>Registration data collected on <span id="registrationDate"></span> (hourly refresh), WG chairs as of <span id="wgChairsDate"></span> (daily refresh), recent draft authors as of <span id="draftAuthorsDate"></span> (daily refresh), by Eric Vyncke based on <a href="https://developers.google.com/chart">Google charts</a>, <a href="https://datatracker.ietf.org/api/">IETF data tracker</a> data, and <a href="https://ourworldindata.org/">https://ourworldindata.org/</a>, itself based on <a href="https://github.com/CSSEGISandData/COVID-19">JHU CSSE COVID-19 Data</a>.
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
