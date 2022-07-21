import requests
import json

email = "EMAIL"
password = "PASSWORD"

def printBreak():
    print("----------------------")

header = '{"Content-Type": "application/x-amz-json-1.1", "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"}'

body = '{"AuthParameters": {"USERNAME": "'+email+'", "PASSWORD": "'+password+'"}, "AuthFlow": "USER_PASSWORD_AUTH", "ClientId": "65knvqta6p37efc2l3eh26pl5o"}'

header = json.loads(header)
body = json.loads(body)

response = requests.post("https://cognito-idp.us-east-1.amazonaws.com/", headers=header, json=body)

token = json.loads(response.content)['AuthenticationResult']['IdToken']

endpoint = "https://api.orangetheory.co/virtual-class/in-studio-workouts"
data = {}
header = {"Content-Type": "application/json", "Authorization": token}

inStudioResponse = requests.get(endpoint, headers=header)

inStudioResponse_json = json.loads(inStudioResponse.content)
memberUuid = inStudioResponse_json['data'][0]['memberUuId']
classTypeCounter = {}
classesByCoach = {}

for item in inStudioResponse_json['data']:
    if item['classType'] == None:
        item['classType'] = "No Class Type Found"
    if item['classType'] in classTypeCounter:
        classTypeCounter[item['classType']] = classTypeCounter[item['classType']] + 1
    else: classTypeCounter[item['classType']] = 1
    studioCoach = item['coach']+"- "+item['studioName']
    if studioCoach in classesByCoach:
        classesByCoach[studioCoach] = classesByCoach[studioCoach] + 1
    else:
        classesByCoach[studioCoach] = 1

print("Number of classes by coach:")
for coach in classesByCoach:

    print(coach+": "+str(classesByCoach[coach]))
printBreak()
print("Classes by type:")
for item in classTypeCounter:
    print(item+": "+str(classTypeCounter[item]))

# print(memberUuid)

memberDetailsUrl = "https://api.orangetheory.co/member/members/"+memberUuid+"?include=memberClassSummary"
# print(memberDetailsUrl)
memberDetaialsResponse = requests.get(memberDetailsUrl, headers=header)
# print(memberDetaialsResponse.content)
memberDetaialsResponse_json = json.loads(memberDetaialsResponse.content)['data']


hrTotals = {}
minCount = {}
secsInZone = {"Red": 0, "Orange": 0, "Green": 0, "Blue": 0, "Black": 0}
dataClassCounter = 0
maxHrAverageTotal = 0
averageHrTotal = 0
averageSplatsTotal = 0
averageCaloriesTotal = 0
for workout in inStudioResponse_json['data']:
    dataClassCounter = dataClassCounter + 1
    count = 1
    for hr in workout['minuteByMinuteHr'].split("[")[1].split("]")[0].split(","):
        if count in hrTotals:
            hrTotals[count] = int(hrTotals[count]) + int(hr)
        else:
            hrTotals[count] = int(hr)
        if count in minCount:
            minCount[count] = minCount[count] + 1
        else:
            minCount[count] = 1
        count = count + 1
    secsInZone['Red'] = secsInZone['Red'] +workout['redZoneTimeSecond']
    secsInZone['Orange'] = secsInZone['Orange'] + workout['orangeZoneTimeSecond']
    secsInZone['Green'] = secsInZone['Green'] + workout['greenZoneTimeSecond']
    secsInZone['Blue'] = secsInZone['Blue'] + workout['blueZoneTimeSecond']
    secsInZone['Black'] = secsInZone['Black'] + workout['blackZoneTimeSecond']
    maxHrAverageTotal = maxHrAverageTotal + workout['maxHr']
    averageHrTotal = averageHrTotal + workout['avgHr']
    averageSplatsTotal = averageSplatsTotal + workout['totalSplatPoints']
    averageCaloriesTotal = averageCaloriesTotal + workout['totalCalories']


printBreak()
print("Home Studio: "+str(memberDetaialsResponse_json['homeStudio']['studioName']))
print("Total classes booked: "+str(memberDetaialsResponse_json['memberClassSummary']['totalClassesBooked']))
print("Total classes attended: "+str(memberDetaialsResponse_json['memberClassSummary']['totalClassesAttended']))
print("Total intro classes: "+str(memberDetaialsResponse_json['memberClassSummary']['totalIntro']))
print("Total OT Live classes booked: "+str(memberDetaialsResponse_json['memberClassSummary']['totalOTLiveClassesBooked']))
print("Total OT Live classes attended: "+str(memberDetaialsResponse_json['memberClassSummary']['totalOTLiveClassesAttended']))
print("Total classes used HRM (Note: I have no idea why this doesn't match total classes attended): "+str(memberDetaialsResponse_json['memberClassSummary']['totalClassesUsedHRM']))
print("Total studios visited: "+str(memberDetaialsResponse_json['memberClassSummary']['totalStudiosVisited']))
print("Max HR: "+str(memberDetaialsResponse_json['maxHr']))

printBreak()
print("The remainder of the data is based on workout summaries available. You have " + str(dataClassCounter) + " workouts with data available")
print("Average Max HR: " + str(maxHrAverageTotal / dataClassCounter))
print("Average HR: " + str(averageHrTotal / dataClassCounter))
print("Average Splats: " + str(averageSplatsTotal / dataClassCounter))
print("Average calorie burn: "+ str(averageCaloriesTotal / dataClassCounter))

printBreak()
print("Average HR by Min:")
for min in minCount:
    average = hrTotals[min] / minCount[min]
    stringBuilder = str(min)+": "+str(average)
    print(stringBuilder)
printBreak()
print("Average time in each zone (Mins)")
print("Red: "+str(secsInZone['Red']/dataClassCounter/60))
print("Orange: "+str(secsInZone['Orange']/dataClassCounter/60))
print("Green: "+str(secsInZone['Green']/dataClassCounter/60))
print("Blue: "+str(secsInZone['Blue']/dataClassCounter/60))
print("Black: "+str(secsInZone['Black']/dataClassCounter/60))
