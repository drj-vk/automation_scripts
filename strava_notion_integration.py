import requests
import datetime
import json

with open('config.json') as f:
    config = json.load(f)
NOTION_API_KEY = config['NOTION_API_KEY']

database_id = config["database_id_strava"]
STRAVA_SECRET = config['STRAVA_SECRET'] 
STRAVA_ACCESS = config['STRAVA_ACCESS'] 
STRAVA_REFRESH = config['STRAVA_REFRESH'] 
STRAVA_ATHLETE_ID = config['STRAVA_ATHLETE_ID'] 

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
base_url = "https://www.strava.com/api/v3"
callback_domain = "localhost"



payload = {
    'client_id': STRAVA_ATHLETE_ID,
    'client_secret': STRAVA_SECRET,
    'refresh_token': STRAVA_REFRESH,
    'grant_type': "refresh_token",
    'f': 'json',
    'scope': 'read_all'
}

print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))

header = {'Authorization': 'Bearer ' + access_token}
param = {'per_page': 200, 'page': 1}
my_dataset = requests.get(activites_url, headers=header, params=param).json()


# Set up the Strava API URL and headers

# Calculate the timestamp for one week ago
one_week_ago = datetime.datetime.now() - datetime.timedelta(weeks=1)
timestamp_one_week_ago = int(one_week_ago.timestamp())



# Define the API endpoint for athlete activities
athlete_activities_url = f"{base_url}/athlete/activities"

# Request the activities from the Strava API
params = {
    "after": timestamp_one_week_ago,
    "per_page": 100,
    "page": 1
}

headers = {
    "Authorization": f"Bearer {access_token}"
}


activities = []



# https://www.strava.com/oauth/authorize?
#     STRAVA_ATHLETE_ID=YOUR_CLIENT_ID&
#     redirect_uri=YOUR_CALLBACK_DOMAIN&
#     response_type=code&
#     scope=YOUR_SCOPE

# http://YOUR_CALLBACK_DOMAIN/?
#     state=&
#     code=AUTHORIZATION_CODE_FROM_STRAVA&
#     scope=YOUR_SCOPE


# https://www.strava.com/oauth/token?
#     client_id=YOUR_CLIENT_ID&
#     client_secret=YOUR_CLIENT_SECRET&
#     code=AUTHORIZATION_CODE_FROM_STRAVA&
#     grant_type=authorization_code

while True:
    response = requests.get(athlete_activities_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data:
        break

    activities.extend(data)
    params["page"] += 1

# Process and print the activities
for activity in activities:
    activity_id = activity["id"]
    name = activity["name"]
    start_date = activity["start_date_local"]
    distance = activity["distance"]
    moving_time = activity["moving_time"]

    print(f"Activity ID: {activity_id}")
    print(f"Name: {name}")
    print(f"Start Date: {start_date}")
    print(f"Distance: {distance} meters")
    print(f"Moving Time: {moving_time} seconds")
    print("------------------------------")
