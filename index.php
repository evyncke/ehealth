<html>
<head>
<title>EU Digital COVID Certificate Decoder</title>
</head>
<body>
<h1>EU Green Certificate (= EU Digital COVID Certificate or corona pass) Online Decoder</h1>
<p>Based on the public EU technical <a href="https://github.com/ehn-dcc-development/hcert-spec/blob/main/hcert_spec.md">specifications</a>, here is a simple decoder of the QR-code, it displays all the information in the Health Certificate QR-code with many technical explanations on the steps. A lot of the technique used by the EU Green Certificate are coming from the <a href="https://ietf.org">IETF</a>. The code itself is heavily based on <a href="https://github.com/ehn-dcc-development/ehn-sign-verify-python-trivial">open source code</a>.</p>

<p>As it appears that some (all ?) states of USA also use QR-code with <a href='https://spec.smarthealth.cards/#protocol-details'>open specifications</a>, the online decoder also works for SMART&reg; Health Cards. And, you can also have a SMART&reg; Health Card example QR-code <a href='?qr=shc'>decoded</a>.</p>

<h2>Online Health Certificate Decoder</h2>
<p>In order to see a QR-code being decoded, you first need to upload a screen shot (.jpg, .png, .gif) of a QR-code and click on the <b>Decode the QR-code</b> button.
<form enctype="multipart/form-data" action="index.php" method="post">
  <!--input type="hidden" name="MAX_FILE_SIZE" value="300000" /-->
  File to upload : <input name="qrfile" type="file" />
  <br/>
  <input type="submit" value="Decode the QR-code" />
</form>
</p>
<p><i>Since this on-line decoder was created in June 2021, there have been daily requests on how to reverse the process. This is of course trivial for any software engineer and there is some code in 
<a href="https://github.com/ehn-dcc-development/ehn-sign-verify-python-trivial">open source code</a>. Of course, the issue is to have a <b>valid</b> signature that is recognized by the verifier ;-)</i>
If you want to try, then go to the <a href="generate.php">generation tool</a> to generate such an example QR-code for the EU Digital Green Certificate but all verification applications won't accept it (I hope!)
as the signature won't be accepted and even without signature verification, the QR-code will obviously be a fake (e.g., it will be red).</p>
<?php
//print_r($_FILES) ; // Array ( [qrfile] => Array ( [name] => Image-1.jpg [type] => [tmp_name] => [error] => 2 [size] => 0 ) )
if (isset($_FILES['qrfile']) and $_FILES['qrfile']['error'] == '') {
	$remote_qrfname = $_FILES['qrfile']['name'] ;
	$local_qrfname = $_FILES['qrfile']['tmp_name'] ;
	$local_file_type = $_FILES['qrfile']['type'] ;
	$local_file_size = $_FILES['qrfile']['size'] ;

	$shell_command = escapeshellcmd("/home/evyncke/ehealth/decode.sh $local_qrfname") ;
	print("<h2>Decoded Health Certificate</h2>") ;
	print("<pre>") ;
	passthru($shell_command, $return_code) ;
	print("</pre>") ;
} else if (isset($_REQUEST['qr']) and $_REQUEST['qr'] == 'shc') {
	print("<h2>Example of a SMART&reg; Health Card</h2>") ;
	print("<p>Here is an example of QR-code for a COVID-19 test provided by the SMART&reg; Health Cards at <a href='https://github.com/smart-on-fhir/health-cards-designs/blob/main/smart_health_card_portal_vaccine.pdf'>https://github.com/smart-on-fhir/health-cards-designs/blob/main/smart_health_card_portal_vaccine.pdf</a>.</p><img src='smarthealthcard.png'><p>It can easily be decoded as:</p>") ;
	print("<pre>") ;
	readfile("/home/evyncke/ehealth/smarthealthcard.log") ;
	print("</pre>") ;
} else {
	print("<h2>Example of a Decoded Health Certificate</h2>") ;
	print("<p>Here is an example of QR-code for a COVID-19 test provided by the Belgium authorities at <a href='https://github.com/ehn-dcc-development/dcc-testdata/raw/main/BE/png/3.png'>https://github.com/ehn-dcc-development/dcc-testdata/raw/main/BE/png/3.png</a>.</p> <img src='https://github.com/ehn-dcc-development/dcc-testdata/raw/main/BE/png/3.png'><p> It can easily be decoded as:</p>") ;
	print("<pre>") ;
	readfile("/home/evyncke/ehealth/BE_example_3.log") ;
	print("</pre>") ;
}
?>
<hr>
<p>Please let me know if you encounter a bug ;-) <a href="mailto:eric@vyncke.org">eric@vyncke.org</a>.</p>
<p><em>All the data that you upload are immediately deleted from the server after being displayed on your browser. The only retained information is your IP address and when you accessed this web site.</em></p>
<!-- Matomo Image Tracker-->
<img referrerpolicy="no-referrer-when-downgrade" src="https://analytics.vyncke.org/matomo.php?idsite=6&amp;rec=1" style="border:0" alt="" />
<!-- End Matomo -->
</body>
</html>
