import json
from botocore.vendored import requests
from datetime import datetime, timedelta
import time

# EDIT THIS SECTION
age = 36
pincodeMode = False
pincodes = ["600001"]

states = ["Tamil Nadu"]
districts = ["Chennai", "Chengalpet"]
num_days = 2
retry = 1
infiniteLoop = False
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
print_flag = 'Y'
districtMap = {}
stateList = []
districtList = []

def lambda_handler(event, context):
    composedRows=""
    districtMap = {}
    stateList = []
    districtList = []
    qParams = event.get("queryStringParameters", "missing")
    if isinstance(qParams, dict):
        states = event.get("queryStringParameters").get("state", "")
        districts = event.get("queryStringParameters").get("district", "") 
        if (pincodeMode == False):  
            # get district code from the input
            statesList = states.split(",")
            districtsList = districts.split(",")
            URL = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
            result = requests.get(URL, headers=header)
            print(result)
            if result.ok:
                response_json = result.json()
                print (response_json)
                if response_json["states"]:
                    for state in response_json["states"]:
                        for ipState in statesList:
                            if (state["state_name"].lower() == ipState.lower()):
                                stateList.append(state["state_id"])
            
            print("state-List:", stateList)
            # parse states and district codes
            URL_BASE = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
            for stateId in stateList:
                URL = URL_BASE + str(stateId)
                result = requests.get(URL, headers=header)
                if result.ok:
                    response_json = result.json()
                    if response_json["districts"]:
                        for district in response_json["districts"]:
                            for ipDistrict in districtsList:
                                if(district["district_name"].lower() == ipDistrict.lower()):
                                    districtList.append(str(district["district_id"]))
                                    districtMap.update({str(district["district_id"]):district["district_name"]})
            
            # overwrite pincodes list with districtList
            pincodes = districtList
            print(pincodes)
        
        actual = datetime.today()
        list_format = [actual + timedelta(days=i) for i in range(num_days)]
        actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]
        
        styleType = '.styled-table {    border-collapse: collapse;    margin: 25px 0;    font-size: 0.9em;    font-family: sans-serif;    min-width: 400px;    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);}.styled-table thead tr {    background-color: #009879;    color: #ffffff;    text-align: left;}.styled-table th,.styled-table td {    padding: 12px 15px;}.styled-table tbody tr {    border-bottom: 1px solid #dddddd;}.styled-table tbody tr:nth-of-type(even) {    background-color: #f3f3f3;}.styled-table tbody tr:last-of-type {    border-bottom: 2px solid #009879;}.styled-table tbody tr.active-row {    font-weight: bold;    color: #009879;}'
       #######################################################
        counter = 0 
        today = datetime.now()
        date_time = today.strftime("%m/%d/%Y, %H:%M:%S")  
        
        print ("INFO: Querying  for Covid vaccine slots as on: " + date_time + " for age <= ", age)
       
       
        for pincode in pincodes:   
            for given_date in actual_dates:
        
                if (pincodeMode == True):
                    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pincode, given_date)
                else:
                    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(pincode, given_date)
                 
                
                result = requests.get(URL, headers=header)
                
            
                if result.ok:
                    response_json = result.json()
                    # print (response_json)
                    if response_json["centers"]:
                        if(print_flag.lower() == 'y'):
                            for center in response_json["centers"]:
                                for session in center["sessions"]:
                                    dist = ""
                                    avDate = ""
                                    name = ""
                                    blkName = ""
                                    feeType = ""
                                    avail = ""
                                    feees = "Free"
                                    vaccine = ""
                                    if (session["min_age_limit"] <= age and session["available_capacity"] > 0) :
                                        if (pincodeMode == False):
                                            print ('District:' + districtMap[pincode])
                                            dist = districtMap[pincode]
                                        else:
                                            print('Pincode: ' + pincode)
                                            dist = pincode
                                        print("Available on: {}".format(given_date))
                                        avDate = given_date
                                        print("\t", center["name"])
                                        name = center["name"]
                                        print("\t", center["block_name"])
                                        blkName = center["block_name"]
                                        print("\t Fee Type: ", center["fee_type"])
                                        feeType = center["fee_type"]
                                        print("\t Availablity : ", session["available_capacity"])
                                        avail = session["available_capacity"]
                                        if(session["vaccine"] != ''):
                                            print("\t Vaccine type: ", session["vaccine"])
                                            vaccine = session["vaccine"]
                                            if "vaccine_fees" in center:
                                                for fee in center["vaccine_fees"]:
                                                    if (fee["vaccine"] == session["vaccine"]):
                                                        print("\t Vaccine Fees: Rs. ", fee["fee"])
                                                        fees = fee["fee"]
                                            
                                                                    
                                                # [session["vaccine"]])
                                        print("\n")
                                        composedRows = composedRows + "<tr><td>" + str(dist) + "</td><td>" + str(avDate) + "</td><td>" + str(name) + "</td><td>" + str(blkName) + "</td><td>" + str(feeType) + "</td><td>" + str(avail) + "</td><td>" + str(vaccine) + "</td><td>" + str(fees) + "</td></tr>"
                                        counter = counter + 1
                else:
                    print("No Response!")
                    
        if counter == 0:
            print("No other Vaccination slot(s) available!")
        else:
            print('\a')
            print(f"INFO: Search Completed and found  {counter} vaccine slot(s)!!")
        #######################################################
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
            "body": '<html><head><style>' + styleType + '</style></head><h1>CoWin Vaccine Search : ' + date_time + '</h1><br><br><table class="styled-table"><th>District</th><th>Date</th><th>Hospital Name</th><th>Branch</th><th>Fee Type</th><th>Available Slots</th><th>Vaccine</th><th>Fees</th>' + composedRows + "</table></html>"
        }
    else:
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
        "body": '<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><style>* {box-sizing: border-box;}body {  margin: 0;  font-family: Arial, Helvetica, sans-serif;}.topnav {  overflow: hidden;  background-color: #e9e9e9;}.topnav a {  float: left;  display: block;  color: black;  text-align: center;  padding: 14px 16px;  text-decoration: none;  font-size: 17px;}.topnav a:hover {  background-color: #ddd;  color: black;}.topnav a.active {  background-color: #2196F3;  color: white;}.topnav .search-container {  float: right;}.topnav input[type=text] {  padding: 6px;  margin-top: 8px;  font-size: 17px;  border: none;}.topnav .search-container button {  float: right;  padding: 6px 10px;  margin-top: 8px;  margin-right: 16px;  background: #ddd;  font-size: 17px;  border: none;  cursor: pointer;}.topnav .search-container button:hover {  background: #ccc;}@media screen and (max-width: 600px) {  .topnav .search-container {    float: none;  }  .topnav a, .topnav input[type=text], .topnav .search-container button {    float: none;    display: block;    text-align: left;    width: 100%;    margin: 0;    padding: 14px;  }  .topnav input[type=text] {    border: 1px solid #ccc;    }}body {  background-image: url("https://atlas-content-cdn.pixelsquid.com/stock-images/syringe-q1DoZk7-600.jpg");}</style></head><script>function myFunction() {    console.log("hello!1");    var xhttp = new XMLHttpRequest();    var searchState = document.getElementById("state").value;var searchDist = document.getElementById("district").value;    xhttp.onreadystatechange = function() {        if (this.readyState == 4 && this.status == 200) {        document.getElementById("my-demo").innerHTML = this.responseText;        }    };    xhttp.open("GET", "https://313h03jm0c.execute-api.ap-south-1.amazonaws.com/default/CoWinIndiaVPC?state="+searchState+"&district="+searchDist, true);    xhttp.send();}</script><body><div class="topnav"><a class="active" href="https://github.com/sktg84/AWSSandbox/blob/main/SongQueryLambdaService"><img src "https://static.thenounproject.com/png/3692351-200.png"/>Search CoWin for vaccine slots </a>  <div class="search-container"> State <input type="text" placeholder="state" name="search" id="state"> District <input type="text" placeholder="district" name="search" id="district">      <button onclick="myFunction()"><i class="fa fa-search"></i></button>      </div></div><div style="padding-left:16px"> <span id="my-demo"><center><img src ="https://www.raps.org/RAPS/media/Education-Events/2020-04-COVID-19-Vaccine-Tracker-500x300-(1).jpg"/><br></center></span></div></body></html>'
        }   
    return resp 
