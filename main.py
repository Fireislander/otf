from os import rename
import requests
import json
import config
import sys
import pandas as pd
import numpy as np


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
            self.token = json.loads(response.content)['AuthenticationResult']['IdToken']
            
            # Get data
            self._get_user_data()

    def _get_user_data(self):
        """
        Gets OTF data 
        """
        # Get class data from OTF
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': self.token
        }
        response = requests.get(self.otf_data_endpoint, headers=headers)
        response.raise_for_status()
        self.class_df = pd.DataFrame.from_records(
            data=json.loads(response.content)['data'], 
            exclude=['classHistoryUuId', 'classId', 'isIntro', 'isLeader', 'memberEmail', 'memberName', 'memberPerformanceId', 'studioAccountUuId', 'version', 'workoutType']
        )

        # Get member summary
        self.member_id = self.class_df.iloc[0]['memberUuId']
        member_url = f"https://api.orangetheory.co/member/members/{self.member_id}?include=memberClassSummary"
        response = requests.get(member_url, headers=headers)
        response.raise_for_status()
        self.member_summary = json.loads(response.content)['data']
        self.class_summary = self.member_summary.pop('memberClassSummary')

    def by_coach(self, ascending=True) -> pd.DataFrame:
        """
        Returns data by coach name sorted by class count. 
        Specify ascending=False to show coaches with most classes first.
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
otf_data = OTFUserData(config.OTF_CLIENT_ID, config.EMAIL, config.PASSWORD, csv_filename='data.csv')
print(otf_data.by_coach(ascending=False))
print(otf_data.by_studio(ascending=False))
print()
