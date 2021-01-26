import json
from botocore.vendored import requests

def lambda_handler(event, context):
    
    #name=event['queryStringParameters']['name']
    qParams=event.get("queryStringParameters","missing")
    styleType = '.styled-table {    border-collapse: collapse;    margin: 25px 0;    font-size: 0.9em;    font-family: sans-serif;    min-width: 400px;    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);}.styled-table thead tr {    background-color: #009879;    color: #ffffff;    text-align: left;}.styled-table th,.styled-table td {    padding: 12px 15px;}.styled-table tbody tr {    border-bottom: 1px solid #dddddd;}.styled-table tbody tr:nth-of-type(even) {    background-color: #f3f3f3;}.styled-table tbody tr:last-of-type {    border-bottom: 2px solid #009879;}.styled-table tbody tr.active-row {    font-weight: bold;    color: #009879;}'
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
            "body": '<html><head><style>table, th, td {  border: 1px solid black;}</style></head><img src="https://static.thenounproject.com/png/2118808-200.png"/><br><b>Usage:</b> https://7fx0vb51sg.execute-api.us-east-1.amazonaws.com/default/tests3hostedsite?q=songName</html>'
        }
    return resp 
   
