<?php
# Copyright 2022-2025 Eric Vyncke, evyncke@cisco.com
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
#"https://www.ietf.org/proceedings/" + lastMeeting + "/bluesheets/" + bluesheetsFilename ;

$meeting = $_REQUEST['meeting'] ;
$sheet = $_REQUEST['sheet'] ;

$file_name = "bluesheets/$sheet" ;

header('Pragma: public');
header('Content-Type: text/plain; charset=utf-8') ;
header('Cache-Control: public') ; # Should also set the max-age & expiration header...

if (file_exists($file_name))  {
  header('Content-Length: ' . filesize($file_name));
  readfile($file_name) ;
} else {
  $text = file_get_contents("https://www.ietf.org/proceedings/$meeting/bluesheets/$sheet") ;
  file_put_contents($file_name, $text) ;
  header('Content-Length: ' . strlen($text)) ;
  print($text) ;
}
?>
