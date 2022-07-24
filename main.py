import requests
import json
import config
import sys
import pandas as pd
import numpy as np

class Objectify(object):
    """
    Creates a class with attributes and values from the provided key-value pairs 
    """    
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

class OTFUserData:

    def __init__(self, client_id=None, username=None, password=None, csv_filename=None):
        """
        Retrieves data for OTF member.
        To get live data, specify client_id, username, and password.
        For testing purposes, you may also load existing csv data by specifying csv_filename.
        """
        self.client_id = client_id
        self.username = username
        self.password = password
        self.csv_filename = csv_filename
        self.otf_data_endpoint = 'https://api.orangetheory.co/virtual-class/in-studio-workouts'
        self.otf_auth_endpoint = 'https://cognito-idp.us-east-1.amazonaws.com/'

        if self.csv_filename is not None:
            self.class_df = pd.read_csv(self.csv_filename)
        else:
            # Get OTF auth token
            headers = {
                'Content-Type': 'application/x-amz-json-1.1', 
                'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
            }
            body = {
                'AuthParameters': {
                    'USERNAME': self.username, 
                    'PASSWORD': self.password
                },
                'AuthFlow': 'USER_PASSWORD_AUTH', 
                'ClientId': client_id
            }
            response = requests.post(self.otf_auth_endpoint, headers=headers, json=body)
            response.raise_for_status()
            response_json = json.loads(response.content)
            self.id_token = response_json['AuthenticationResult']['IdToken']
            self.access_token = response_json['AuthenticationResult']['AccessToken']
            
            # Get data
            self._get_user_data()
            self._get_class_data()

    def _get_user_data(self):
        """
        Gets OTF user data 
        """
        # Get user data from OTF and objectify into user_attributes
        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.GetUser'           
        }
        body = {
            'AccessToken': self.access_token
        }
        response = requests.post(self.otf_auth_endpoint, headers=headers, json=body)
        response.raise_for_status()
        
        # To convert the user attributes to an object, we create a dictionary of all attributes and values 
        user_attrs = {attr['Name']: attr['Value'] for attr in json.loads(response.content)['UserAttributes']}
        user_attrs['user_id'] = json.loads(response.content)['Username']

        # Then we clean dictionary key names because some of them contain invalid characters like ':'
        user_attrs_clean = dict((k.replace(':', '_'), v) for k, v in user_attrs.items())
        
        # Then convert the clean dictionary to an object 
        self.user_attributes = Objectify(**user_attrs_clean)

        # Get member data
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': self.id_token
        }
        member_url = f"https://api.orangetheory.co/member/members/{self.user_attributes.user_id}?include=memberClassSummary"
        response = requests.get(member_url, headers=headers)
        response.raise_for_status()
        
        # Objectify appropriately
        member_data = json.loads(response.content)['data']
        self.class_summary = Objectify(**member_data.pop('memberClassSummary'))
        self.home_studio = Objectify(**member_data.pop('homeStudio'))
        self.member_profile = Objectify(**member_data.pop('memberProfile'))
        self.member_data = Objectify(**member_data)

    def _get_class_data(self):
        """
        Gets OTF class data 
        """
        # Get class data from OTF
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': self.id_token
        }
        response = requests.get(self.otf_data_endpoint, headers=headers)
        response.raise_for_status()
        self.class_df = pd.DataFrame.from_records(
            data=json.loads(response.content)['data'], 
            exclude=['classHistoryUuId', 'classId', 'isIntro', 'isLeader', 'memberEmail', 'memberName', 'memberPerformanceId', 'studioAccountUuId', 'version', 'workoutType']
        )

    def by_coach(self, ascending=True, merge_similar=False) -> pd.DataFrame:
        """
        Returns data by coach name sorted by class count. 
        Specify ascending=False to show coaches with most classes first.
        Specify merge_similar=True to combine similar coach names into one.
        """
        pivot = self.class_df.pivot_table(
            index='coach',
            values='memberUuId',
            aggfunc=np.count_nonzero
        ).rename(columns={'memberUuId': 'class count'}).sort_values(by='class count', ascending=ascending)
        return pivot

    def by_studio(self, ascending=True) -> pd.DataFrame:
        """
        Returns data by studio name sorted by class count. 
        Specify ascending=False to show studios with most classes first.
        """
        pivot = self.class_df.pivot_table(
            index='studioName',
            values='memberUuId',
            aggfunc=np.count_nonzero
        ).rename(columns={'memberUuId': 'class count'}).sort_values(by='class count', ascending=ascending)
        return pivot


################
# MAIN PROGRAM #
################

otf_data = OTFUserData(config.OTF_CLIENT_ID, config.EMAIL, config.PASSWORD)
print(otf_data.by_coach(ascending=False))
print(otf_data.by_studio(ascending=False))
print()
