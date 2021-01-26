import json
from botocore.vendored import requests

#Credits to https://sysadmins.co.za/tutorial-on-dynamodb-using-bash-and-the-aws-cli-tools-to-interact-with-a-music-dataset/
def lambda_handler(event, context):
    
    #name=event['queryStringParameters']['name']
    qParams=event.get("queryStringParameters","missing")
    if isinstance(qParams, dict):
        name=event.get("queryStringParameters").get("name","")
        url = 'https://itunes.apple.com/search?term='+name+'&limit=100'
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
            composedRows = composedRows + "<tr><td>"+songName+"</td><td>"+"  <img src=\""+albumArt+"\"/>"+"</td><td>"+album+"</td><td>"+artist+"</td><td><embed src=\""+link+"\"/></td></tr>"
        
    
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
            "body": "<html><head><style>table, th, td {  border: 1px solid black;}</style></head><table >"+composedRows+"</table></html>"
        }
    else:
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
            "body": '<html><head><style>table, th, td {  border: 1px solid black;}</style></head><img src="https://static.thenounproject.com/png/2118808-200.png"/><br><b>Usage:</b> https://7fx0vb51sg.execute-api.us-east-1.amazonaws.com/default/tests3hostedsite?name=songName</html>'
        }
    return resp 
