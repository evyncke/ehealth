<html>
<head>
<title>EU Digital COVID Certificate Generation (for test)</title>
</head>
<body>
<h1>EU Green Certificate (= EU Digital COVID Certificate or corona pass) Online QR code generation for tests</h1>
<p>Based on the public EU technical <a href="https://github.com/ehn-dcc-development/hcert-spec/blob/main/hcert_spec.md">specifications</a>, here is a simple encoder of the QR-code, it describes also the many technical explanations on the steps.</p>
<p> A lot of the techniques used by the EU Green Certificate are coming from the <a href="https://ietf.org">IETF</a>. The code itself is heavily based on <a href="https://github.com/ehn-dcc-development/ehn-sign-verify-python-trivial">open source code</a>.</p>

<p><em>The only purpose of this page is to show that there is <b>no magic</b> behind the QR-code itself. The generated QR will be detected as <b>invalid</b> by any good validator because:
<ul>
<li>a human being will notice the 'FAKE' logo in the middle of the QR code;</li>
<li>a human being will find strange that the QR code background is red;</li>
<li>the COSE claims are expired since yesterday;</li>
<li>the key used to sign the COSE Web Token is not trusted (as I generated with openssl locally);</li>
<li>the date of birth is in the XIXth century;</li>
<li>this issuer name will please Harry Potter's fans;</li>
<li>your IP address is encoded in the opaque part of 'unique certificate identifier';</li>
<li>a "fake for test" is inserted after the 'test center'.</li>
</ul>
</em>
</p>

<h2>Online Health Certificate Encoder/Generator</h2>
<p>The first step is to build the health payload using a JSON format based on the input you provided. You may notice that some values have been changed in order to clearly identify this QR code as a fake/test one. The encoding
is based on <a href="https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf">https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf</a>, e.g.:
<ul>
<li><b>dob</b>: date of birth;</li>
<li><b>fn</b>: family/surname name, which also translated to the ICAO machine readable format as <b>fnt</b>:;</li>
<li><b>gn</b>: given/first name, which also translated to the ICAO machine readable format as <b>gnt</b>:;</li>
<li><b>t</b>: this is for a <b>test</b>:
<ul>
	<li><b>co</b>: country where the test was carried;</li>
	<li><b>tg</b>: target disease (in this case COVID-19);</li>
	<li><b>tt</b>: test type code;</li>
	<li><b>tr</b>: test result;</li>
	<li><b>tc</b>: test center;</li>
	<li><b>sc</b>: sample collection (date and time in UTC);</li>
	<li><b>ma</b>: manufacturer code for rapid antigen tests;</li>
	<li><b>nm</b>: test name.</li>
</ul>
</ul></p>
<?php
if (isset($_REQUEST['action']) and $_REQUEST['action'] == 'Generate') {
	if (strlen($_REQUEST['co']) != 2) die("Invalid country data") ;
	if (strlen($_REQUEST['fn']) <= 1) die("Invalid family name data") ;
	if (strlen($_REQUEST['gn']) <= 1) die("Invalid given name data") ;
	setlocale(LC_CTYPE, 'en_GB'); // Seems to be required for iconv() to work...
	$health_payload = array() ;
	$health_payload['ver'] = '1.3.0' ;
	$health_payload['dob'] = '18' . substr($_REQUEST['dob'], 2) ;
	$health_payload['nam'] = array() ;
	$health_payload['nam']['fn'] = $_REQUEST['fn'] ;
	$health_payload['nam']['fnt'] = strtoupper(iconv('UTF-8', 'ASCII//TRANSLIT', $_REQUEST['fn'])) ;
	$health_payload['nam']['gn'] = $_REQUEST['gn'] ;
	$health_payload['nam']['gnt'] = strtoupper(iconv('UTF-8', 'ASCII//TRANSLIT', $_REQUEST['gn'])) ;
	$health_payload['t'] = array() ;
	$health_payload['t'][0] = array() ;
	$health_payload['t'][0]['co'] = $_REQUEST['co'] ;
	$health_payload['t'][0]['tg'] = $_REQUEST['tg'] ;
	$health_payload['t'][0]['tt'] = $_REQUEST['tt'] ;
	$health_payload['t'][0]['tr'] = $_REQUEST['tr'] ;
	$health_payload['t'][0]['tc'] = $_REQUEST['tc'] . ' (fake for a test)' ;
	$health_payload['t'][0]['sc'] = $_REQUEST['sc'] . 'T' . gmstrftime('%X') . 'Z' ;
	if ($_REQUEST['tt'] == 'LP217198-3') // Rapid immunoassay
		$health_payload['t'][0]['ma'] = $_REQUEST['ma'] ;
	else
		$health_payload['t'][0]['nm'] = 'Fake test ehealth.vyncke.org' ;
	$health_payload['t'][0]['is'] = 'Ministry of Magic Health, Whitehall, London' ;
	$health_payload['t'][0]['ci'] = 'URN:UVCI:01:' . $_REQUEST['co'] . ':' . strtoupper(str_replace(array('.', ':'), 'Z', $_SERVER['REMOTE_ADDR'])) ; 
	$json_string = json_encode($health_payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
	print("<h3>Health Payload</h3><pre>$json_string</pre>") ;
	$hash = md5($json_string) ;
	file_put_contents("/tmp/$hash.json", $json_string) ;
	$shell_command = escapeshellcmd("/home/evyncke/ehealth/encode.sh /tmp/$hash $_REQUEST[co]") ;
	print("<pre>") ;
	passthru("$shell_command 2>&1", $return_code) ;
	print("</pre>") ;
?>
<h3>Final QR code</h3>
<a href="qrcode.php?id=<?=$hash?>"><img src="qrcode.php?id=<?=$hash?>"></a>
<?php
	$headers['From'] = 'qrcode@vyncke.org' ;
	$headers['MIME-Version'] = '1.0' ;
	$headers['Content-type'] = 'text/plain; charset=utf-8' ;
//	@mail('eric.vyncke@uliege.be', 'QR generation', "$_SERVER[REMOTE_ADDR] a $_SERVER[USER_AGENT] has generated:\n$json_string", $headers) ;
} else {
	// Try to build the JSON payload
// {
//         "dob": "1960-07-26",
//         "nam": {
//                 "fn": "Vyncke",
//                 "fnt": "VYNCKE",
//                 "gn": "Eric",
//                 "gnt": "ERIC"
//         },
//         "v": [
//                 {
//                         "ci": "01BEWACCCGRDITMO6IYQAQB2PFAT#E",
//                         "co": "BE",
//                         "dn": 1,
//                         "dt": "2021-04-26",
//                         "is": "AVIQ",
//                         "ma": "ORG-100001699",
//                         "mp": "EU/1/21/1529",
//                         "sd": 2,
//                         "tg": "840539006",
//                         "vp": "1119305005"
//                 }
//         ],
//         "ver": "1.0.1"
//         }
?>
<form method='post' accept-charset="utf-8">
<label for='gn'>First/Given name:</label>
<input type='text' id='gn' name='gn'><br/>
<label for='fn'>Last/Family name:</label>
<input type='text' id='fn' name='fn'><br/>
<label for='dob'>Date of birth:</label>
<input type='date' id='dob' name='dob'><br/>
<label for='co'>Country:</label>
<select name='co' id='co'>
<?php
	$json = file_get_contents("country-2-codes.json") ;
	$countries = json_decode($json, true) ;
	foreach ($countries['valueSetValues'] as $cn => $dict) {
		print("<option value='$cn'>$dict[display]</option> ") ;
	 }
?>
</select><br/>
<label for='tt'>Test type:</label>
<select name='tt' id='tt'></label>
<?php
	$json = file_get_contents("test-type.json") ;
	$test_types = json_decode($json, true) ;
	foreach ($test_types['valueSetValues'] as $tt => $dict) {
		print("<option value='$tt'>$dict[display]</option> ") ;
	 }
?>
</select>
<label for='ma'>Test manufacturer (only if rapid test):</label>
<select name='ma' id='ma'></label>
<?php
	$json = file_get_contents("test-manf.json") ;
	$test_manufacturers = json_decode($json, true) ;
	foreach ($test_manufacturers['valueSetValues'] as $ma => $dict) {
		print("<option value='$ma'>$dict[display]</option> ") ;
	 }
?>
</select></br>
<label for='tc'>Test center:</label>
<input type='text' id='tc' name='tc' size=70 maxlength=70><br/>
<label for='sc'>Date of test:</label>
<input type='date' id='sc' name='sc'><br/>
<label for='tr'>Test result:</label>
<select name='tr'>
<?php
	$json = file_get_contents("test-result.json") ;
	$test_results = json_decode($json, true) ;
	foreach ($test_results['valueSetValues'] as $tr => $dict) {
		print("<option value='$tr'>$dict[display]</option> ") ;
	 }
?>
</select></br>
<input type='hidden' name='tg' value='840539006'><!-- the coded value for COVID-19, hardcoded as there is only one choice! -->
<input type='submit' name='action' value='Generate'>
</form>
<?php
} // end of JSON payload building
?>
<hr>
<p>Please let me know if you encounter a bug ;-) <a href="mailto:eric@vyncke.org">eric@vyncke.org</a>.</p>
<p><em>All the data that you upload are immediately deleted from the server after being displayed on your browser. The only retained information is your IP address and when you accessed this web site.</em></p>
<!-- Matomo Image Tracker-->
<img referrerpolicy="no-referrer-when-downgrade" src="https://analytics.vyncke.org/matomo.php?idsite=6&amp;rec=1" style="border:0" alt="" />
<!-- End Matomo -->
</body>
</html>
