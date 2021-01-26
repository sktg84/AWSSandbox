import json
from botocore.vendored import requests

def lambda_handler(event, context):
    
    #name=event['queryStringParameters']['name']
    qParams=event.get("queryStringParameters","missing")
    styleType = '.styled-table {    border-collapse: collapse;    margin: 25px 0;    font-size: 0.9em;    font-family: sans-serif;    min-width: 400px;    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);}.styled-table thead tr {    background-color: #009879;    color: #ffffff;    text-align: left;}.styled-table th,.styled-table td {    padding: 12px 15px;}.styled-table tbody tr {    border-bottom: 1px solid #dddddd;}.styled-table tbody tr:nth-of-type(even) {    background-color: #f3f3f3;}.styled-table tbody tr:last-of-type {    border-bottom: 2px solid #009879;}.styled-table tbody tr.active-row {    font-weight: bold;    color: #009879;}'
    #styleType = 'html,body {	height: 100%;}body {	margin: 0;	background: linear-gradient(45deg, #49a09d, #5f2c82);	font-family: sans-serif;	font-weight: 100;}.container {	position: absolute;	top: 50%;	left: 50%;	transform: translate(-50%, -50%);}table {	width: 800px;	border-collapse: collapse;	overflow: hidden;	box-shadow: 0 0 20px rgba(0,0,0,0.1);}th,td {	padding: 15px;	background-color: rgba(255,255,255,0.2);	color: #fff;}th {	text-align: left;}thead {	th {		background-color: #55608f;	}}tbody {	tr {		&:hover {			background-color: rgba(255,255,255,0.3);		}	}	td {		position: relative;		&:hover {			&:before {				content: "";				position: absolute;				left: 0;				right: 0;				top: -9999px;				bottom: -9999px;				background-color: rgba(255,255,255,0.2);				z-index: -1;			}		}	}}'
    if isinstance(qParams, dict):
        name=event.get("queryStringParameters").get("q","")
        url = 'https://itunes.apple.com/search?term='+name+'&limit=25'
        urlResp = requests.get(url).json()
        print(json.dumps(urlResp, indent=2))
        retVal= json.dumps(urlResp, indent=2)
        composedRows=""
        for item in urlResp["results"]:
            artist = item.get("artistName","Unknown")
            album = item.get("collectionName","Single")
            songName = item.get("trackName","Unknown")
            link = item.get("previewUrl","NA")
            albumArt = item.get("artworkUrl100","https://static.thenounproject.com/png/2118808-200.png")
            composedRows = composedRows + "<tr><td>"+songName+"</td><td>"+"  <img src=\""+albumArt+"\"/>"+"</td><td>"+album+"</td><td>"+artist+"</td><td><audio controls> <source src=\""+link+"\"></audio>"+"</td></tr>"
        
    
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
            "body": '<html><head><style>'+styleType+'</style></head><h1>Top 25 Songs for the search: '+name+'</h1><br><br><table class="styled-table"><th>Track Name</th><th>Album Art</th><th>Album Name</th><th>Artist</th><th>Sample Track</th>'+composedRows+"</table></html>"
        }
    else:
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
            #"body": '<html><head><style>table, th, td {  border: 1px solid black;}</style></head><img src="https://static.thenounproject.com/png/2118808-200.png"/><br><b>Usage:</b> https://7fx0vb51sg.execute-api.us-east-1.amazonaws.com/default/tests3hostedsite?q=songName</html>'
            "body": '<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><style>* {box-sizing: border-box;}body {  margin: 0;  font-family: Arial, Helvetica, sans-serif;}.topnav {  overflow: hidden;  background-color: #e9e9e9;}.topnav a {  float: left;  display: block;  color: black;  text-align: center;  padding: 14px 16px;  text-decoration: none;  font-size: 17px;}.topnav a:hover {  background-color: #ddd;  color: black;}.topnav a.active {  background-color: #2196F3;  color: white;}.topnav .search-container {  float: right;}.topnav input[type=text] {  padding: 6px;  margin-top: 8px;  font-size: 17px;  border: none;}.topnav .search-container button {  float: right;  padding: 6px 10px;  margin-top: 8px;  margin-right: 16px;  background: #ddd;  font-size: 17px;  border: none;  cursor: pointer;}.topnav .search-container button:hover {  background: #ccc;}@media screen and (max-width: 600px) {  .topnav .search-container {    float: none;  }  .topnav a, .topnav input[type=text], .topnav .search-container button {    float: none;    display: block;    text-align: left;    width: 100%;    margin: 0;    padding: 14px;  }  .topnav input[type=text] {    border: 1px solid #ccc;    }}body {  background-image: url("https://images.unsplash.com/photo-1488109811119-98431feb6929?ixlib=rb-1.2.1&ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&auto=format&fit=crop&w=1700&q=80");}</style></head><script>function myFunction() {	console.log("hello!1");    var xhttp = new XMLHttpRequest();	var searchStr = document.getElementById("search").value;    xhttp.onreadystatechange = function() {        if (this.readyState == 4 && this.status == 200) {        document.getElementById("my-demo").innerHTML = this.responseText;        }    };    xhttp.open("GET", "https://7fx0vb51sg.execute-api.us-east-1.amazonaws.com/default/tests3hostedsite?q="+searchStr, true);    xhttp.send();}</script><body><div class="topnav"><a class="active" href="https://github.com/sktg84/AWSSandbox/blob/main/SongQueryLambdaService"><img src "https://static.thenounproject.com/png/3692351-200.png"/>Search Songs From Apple iTunes</a>  <div class="search-container">      <input type="text" placeholder="Search.." name="search" id="search">      <button onclick="myFunction()"><i class="fa fa-search"></i></button>      </div></div><div style="padding-left:16px"> <span id="my-demo"><center><img src ="https://static.thenounproject.com/png/2644705-200.png"/><br><h1>Search with the search bar !!</h1></center></span></div></body></html>'
        }   
    return resp 
