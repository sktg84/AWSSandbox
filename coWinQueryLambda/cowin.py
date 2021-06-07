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
        age = int(event.get("queryStringParameters").get("age", ""))
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
            "body": '<html><head><style>' + styleType + '</style></head><h3>CoWin Vaccine Search for today & tomorrow as on: ' + date_time + ' GMT/UTC</h3><br><br><table class="styled-table"><th>District</th><th>Date</th><th>Hospital Name</th><th>Branch</th><th>Fee Type</th><th>Available Slots</th><th>Vaccine</th><th>Fees</th>' + composedRows + "</table></html>"
        }
    else:
        resp = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'text/html',  # added for making a table
            },
        "body": '<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><style>* {box-sizing: border-box;}body {  margin: 0;  font-family: Arial, Helvetica, sans-serif;}.topnav {  overflow: hidden;  background-color: #e9e9e9;}.topnav a {  float: left;  display: block;  color: black;  text-align: center;  padding: 14px 16px;  text-decoration: none;  font-size: 17px;}.topnav a:hover {  background-color: #ddd;  color: black;}.topnav a.active {  background-color: #2196F3;  color: white;}.topnav .search-container {  float: right;}.topnav input[type=text] {  padding: 6px;  margin-top: 8px;  font-size: 17px;  border: none;}.topnav .search-container button {  float: right;  padding: 6px 10px;  margin-top: 8px;  margin-right: 16px;  background: #ddd;  font-size: 17px;  border: none;  cursor: pointer;}.topnav .search-container button:hover {  background: #ccc;}@media screen and (max-width: 600px) {  .topnav .search-container {    float: none;  }  .topnav a, .topnav input[type=text], .topnav .search-container button {    float: none;    display: block;    text-align: left;    width: 100%;    margin: 0;    padding: 14px;  }  .topnav input[type=text] {    border: 1px solid #ccc;    }}body {  background-image: url("https://africa-images.com/public/photos/4/U/4U2E0qq9LorslBtNDwo8dq4E0/4U2E0qq9LorslBtNDwo8dq4E0_smaller.jpg");  background-size: cover;}</style></head><script>function myFunction() {    console.log("hello!1");    var xhttp = new XMLHttpRequest();    var searchState = document.getElementById("state").value;var searchDist = document.getElementById("district").value;var searchAge = document.getElementById("age").value;    xhttp.onreadystatechange = function() {        if (this.readyState == 4 && this.status == 200) {        document.getElementById("my-demo").innerHTML = this.responseText;        }    };    xhttp.open("GET", "https://313h03jm0c.execute-api.ap-south-1.amazonaws.com/default/CoWinIndiaVPC?state="+searchState+"&district="+searchDist+"&age="+searchAge, true);    xhttp.send();}var stateObject = {"India": {"Andaman and Nicobar Islands": ["Nicobar", "North and Middle Andaman", "South Andaman"], "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Prakasam", "Sri Potti Sriramulu Nellore", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR District, Kadapa (Cuddapah)"], "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Itanagar Capital Complex", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"], "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup Metropolitan", "Kamrup Rural", "Karbi-Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"], "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"], "Chandigarh": ["Chandigarh"], "Chhattisgarh": ["Balod", "Baloda bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Gaurela Pendra Marwahi", "Janjgir-Champa", "Jashpur", "Kanker", "Kawardha", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"], "Dadra and Nagar Haveli": ["Dadra and Nagar Haveli"], "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"], "Goa": ["North Goa", "South Goa"], "Gujarat": ["Ahmedabad", "Ahmedabad Corporation", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Bhavnagar Corporation", "Botad", "Chhotaudepur", "Dahod", "Dang", "Devbhumi Dwaraka", "Gandhinagar", "Gandhinagar Corporation", "Gir Somnath", "Jamnagar", "Jamnagar Corporation", "Junagadh", "Junagadh Corporation", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Rajkot Corporation", "Sabarkantha", "Surat", "Surat Corporation", "Surendranagar", "Tapi", "Vadodara", "Vadodara Corporation", "Valsad"], "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurgaon", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"], "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"], "Jammu and Kashmir": ["Anantnag", "Bandipore", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"], "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"], "Karnataka": ["Bagalkot", "Bangalore Rural", "Bangalore Urban", "BBMP", "Belgaum", "Bellary", "Bidar", "Chamarajanagar", "Chikamagalur", "Chikkaballapur", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Gulbarga", "Hassan", "Haveri", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysore", "Raichur", "Ramanagara", "Shimoga", "Tumkur", "Udupi", "Uttar Kannada", "Vijayapura", "Yadgir"], "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"], "Ladakh": ["Kargil", "Leh"], "Lakshadweep": ["Agatti Island", "Lakshadweep"], "Madhya Pradesh": ["Agar", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"], "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"], "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"], "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri-Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"], "Mizoram": ["Aizawl East", "Aizawl West", "Champhai", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Serchhip", "Siaha"], "Nagaland": ["Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Peren", "Phek", "Tuensang", "Wokha", "Zunheboto"], "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khurda", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"], "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"], "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozpur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Pathankot", "Patiala", "Rup Nagar", "Sangrur", "SAS Nagar", "SBS Nagar", "Sri Muktsar Sahib", "Tarn Taran"], "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur I", "Jaipur II", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"], "Sikkim": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"], "Tamil Nadu": ["Aranthangi", "Ariyalur", "Attur", "Chengalpet", "Chennai", "Cheyyar", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram", "Kanyakumari", "Karur", "Kovilpatti", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", "Nilgiris", "Palani", "Paramakudi", "Perambalur", "Poonamallee", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Sivakasi", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi (Tuticorin)", "Tiruchirappalli", "Tirunelveli", "Tirupattur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"], "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal(Rural)", "Warangal(Urban)", "Yadadri Bhuvanagiri"], "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"], "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Badaun", "Baghpat", "Bahraich", "Balarampur", "Ballia", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnour", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"], "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"], "West Bengal": ["Alipurduar District", "Bankura", "Basirhat HD (North 24 Parganas)", "Birbhum", "Bishnupur HD (Bankura)", "Cooch Behar", "COOCHBEHAR", "Dakshin Dinajpur", "Darjeeling", "Diamond Harbor HD (S 24 Parganas)", "East Bardhaman", "Hoogly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "Nandigram HD (East Medinipore)", "North 24 Parganas", "Paschim Medinipore", "Purba Medinipore", "Purulia", "Rampurhat HD (Birbhum)", "South 24 Parganas", "Uttar Dinajpur", "West Bardhaman"], "Daman and Diu": ["Daman", "Diu"]}}; window.onload = function () { var countySel = document.getElementById("country"), stateSel = document.getElementById("state"), districtSel = document.getElementById("district"); for (var country in stateObject) { countySel.options[countySel.options.length] = new Option(country, country); } countySel.onchange = function () { stateSel.length = 1;  districtSel.length = 1;  if (this.selectedIndex < 1) {return;}  for (var state in stateObject[this.value]) { stateSel.options[stateSel.options.length] = new Option(state, state); } } ;countySel.onchange();  stateSel.onchange = function () { districtSel.length = 1;  if (this.selectedIndex < 1) {return;} var district = stateObject[countySel.value][this.value]; for (var i = 0; i < district.length; i++) { districtSel.options[districtSel.options.length] = new Option(district[i], district[i]); } } }</script><body><div class="topnav"><a class="active" href="https://github.com/sktg84/AWSSandbox/tree/main/coWinQueryLambda"><img src "https://www.raps.org/RAPS/media/Education-Events/2020-04-COVID-19-Vaccine-Tracker-500x300-(1).jpg"/>Search CoWin for vaccine slots </a> <a href="https://github.com/sktg84/AWSSandbox/blob/main/coWinQueryLambda/README.md"><span>&#8505;</span></a> <div class="search-container"> Age: <input type="text" placeholder="Age" name="search" id="age" size="4">   Country: <select name="state" id="country" size="1"><option value="" selected="selected">Select Country</option></select>   State: <select name="countrya" id="state" size="1"><option value="" selected="selected">Please select Country first</option></select>   District: <select name="district" id="district" size="1"><option value="" selected="selected">Please select State first</option></select>  <button onclick="myFunction()"><i class="fa fa-search"></i></button>      </div></div><div style="padding-left:16px"> <span><center>&#9997;Karthik Subramanian, 2021.</center></span><br><span id="my-demo"><center><img src ="https://covid19.trackvaccines.org/wp-content/uploads/2020/09/new-logo-draft.png"/><br></center></span></div></body></html>'
        }   
    return resp 
