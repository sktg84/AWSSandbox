# [CoWin-Vaccine-Notifier]()
Automated Lambda Script to retrieve vaccine slots availability...
URL: https://313h03jm0c.execute-api.ap-south-1.amazonaws.com/default/CoWinIndiaVPC
## Step 1:
  Pick a state from the URL: 
  
  https://cdn-api.co-vin.in/api/v2/admin/location/states
  
  Example:
  Lets pick Tamil Nadu (Note the space). It has a state_id of <b>31</b>
  ```
  {
states: [
{
state_id: 1,
state_name: "Andaman and Nicobar Islands"
},
{
state_id: 2,
state_name: "Andhra Pradesh"
},
...
...
{
state_id: 31,
state_name: "Tamil Nadu"
},
...
...
{
state_id: 36,
state_name: "West Bengal"
}
],
ttl: 24
}
  ```
  
 ## Step 2:
  Pick a district from the URL by passing the state_id picked from Step 1. 
  
  https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state_id>
  
  Example:
   
    https://cdn-api.co-vin.in/api/v2/admin/location/districts/31
    
  
 Response for the above call would be like the one below. Use the district name as in "district_name": like <b>Chennai</b>
```    
   {
    districts: [
    {
    district_id: 779,
    district_name: "Aranthangi"
    },
    ...
    ...
    {
    district_id: 565,
    district_name: "Chengalpet"
    },
    {
    district_id: 571,
    district_name: "Chennai"
    },
    ...
    ...
    {
    district_id: 549,
    district_name: "Virudhunagar"
    }
    ],
    ttl: 24
    }
```

This project is licensed under the MIT License
<h3 align="center">Show some &nbsp;❤️&nbsp; by starring some of the repositories!</h3>
