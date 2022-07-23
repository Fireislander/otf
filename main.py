import requests
import json
import config
import sys
import pandas as pd

# Get OTF auth token
headers = {
    'Content-Type': 'application/x-amz-json-1.1', 
    'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
}
body = {
    'AuthParameters': {
        'USERNAME': config.EMAIL, 
        'PASSWORD': config.PASSWORD
    },
    'AuthFlow': 'USER_PASSWORD_AUTH', 
    'ClientId': config.OTF_CLIENT_ID
}
try:
    print('Connecting to OTF...')
    response = requests.post('https://cognito-idp.us-east-1.amazonaws.com/', headers=headers, json=body)
    response.raise_for_status()
except Exception as e:
    print(str(e))
    sys.exit()

token = json.loads(response.content)['AuthenticationResult']['IdToken']

# Get data
endpoint = 'https://api.orangetheory.co/virtual-class/in-studio-workouts'
headers = {
    'Content-Type': 'application/json', 
    'Authorization': token
}
try:
    print('Getting data...')
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
except Exception as e:
    print(str(e))
    sys.exit()

# Get the data into a DataFrame so that we can easily analyze it
df = pd.DataFrame.from_dict(json.loads(response.content)['data'])
for index, row in df.iterrows():
    row['workoutType'] = row['workoutType']['displayName']

# Get member summary
member_id = df.iloc[0]['memberUuId']
member_url = f"https://api.orangetheory.co/member/members/{member_id}?include=memberClassSummary"
try:
    print('Getting member symmary...')
    response = requests.get(member_url, headers=headers)
    response.raise_for_status()
except Exception as e:
    print(str(e))
    sys.exit()
member_summary = json.loads(response.content)['data']
class_summary = member_summary['memberClassSummary']

