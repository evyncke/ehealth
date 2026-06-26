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
# Bypassing the CORS restrictions when using the DT proxy API from a browser

header("Access-Control-Allow-Origin: *");
$url = $_GET['url'];
echo file_get_contents("https://www.ietf.org/" . $url);
?>