"""
Create a config.py file and specify OTF_CLIENT_ID, EMAIL, and PASSWORD
"""
import config
from otf_user_data import OTFUserData

################
# MAIN PROGRAM #
################

otf_data = OTFUserData(config.OTF_CLIENT_ID, config.EMAIL, config.PASSWORD)
print('Class Summary')
print('=============')
for k, v in vars(otf_data.class_summary).items():
    print(f"{k}: {v}")
print()
print('Classes by Coach')
print('================')
print(otf_data.by_coach(ascending=False))
print()
print('Classes by Studio')
print('=================')
print(otf_data.by_studio(ascending=False))

