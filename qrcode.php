<?php
if (! isset($_REQUEST['id'])) die("Missing parameter") ;

$name="/tmp/$_REQUEST[id].png" ;
$real_path = realpath($name) ;
if ($real_path === false || strpos($real_path, realpath('/tmp')) !== 0)
	die('Directory traversal not allowed') ;
header("Content-Type: image/png");
header("Content-Length: " . filesize($name));

$fp = fopen($name, 'rb');
fpassthru($fp);
exit;

?>
