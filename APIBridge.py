import requests

API_KEY = 'ce05ba202aa14a13875966f46846ef98'

def getProfilesFromMicrosoft():
    request = requests.get('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles',
                           headers = {
                               'Ocp-Apim-Subscription-Key': API_KEY
                           })

    return request.json()


def createMicrosoftProfile():
    request = requests.post('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles',
                           headers={
                               'Ocp-Apim-Subscription-Key': API_KEY
                           },
                            data = {
                                "locale": "en-us"
                            })

    return request.json()['identificationProfileId']

def createMicrosoftEnrollment(profileID, audioFilePath):
    request = requests.post('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles/%s/enroll' % profileID,
                            headers={
                                'Ocp-Apim-Subscription-Key': API_KEY
                            },
                            files = {
                                "file": open(audioFilePath, "rb")
                            })

    return request.status_code

def identifySpeaker(audioFilePath, candidateIDs):
    idString = ','.join(candidateIDs)

    request = requests.post(
        'https://westus.api.cognitive.microsoft.com/spid/v1.0/identify?identificationProfileIds=%s&shortAudio=True' % idString,
        headers={
            'Ocp-Apim-Subscription-Key': API_KEY
        },
        files={
            "file": open(audioFilePath, "rb")
        })

    return request.headers['Operation-Location']

def getMicrosoftOperationResult(requestUrl):
    request = requests.get(requestUrl,
                            headers={
                                'Ocp-Apim-Subscription-Key': API_KEY
                            })

    json = request.json()
    if json['status'] == "notstarted" or json['status'] == "running":
        return getMicrosoftOperationResult(requestUrl)
    elif json['status'] == "failed":
        raise AssertionError("Failed to Execute Operation")

    return json

def deleteMicrosoftProfile(profileID):
    request = requests.delete(
        'https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles/%s' % profileID,
        headers={
            'Ocp-Apim-Subscription-Key': API_KEY
        })

    return request.status_code

#createMicrosoftProfile()
#createMicrosoftEnrollment(createMicrosoftProfile(), "audiosamples/enrol-royo.wav")
#getProfilesFromMicrosoft()
#createMicrosoftEnrollment("ac25bd0b-7340-43e3-ae81-662fe571ac14", "audiosamples/enrol-ricky.wav")
profiles = list(map(lambda x: x['identificationProfileId'], getProfilesFromMicrosoft()))
for profile in profiles:
    deleteMicrosoftProfile(profile)
#identifySpeaker('audiosamples/enrol-luis.wav', profiles)
#statusUrl = identifySpeaker('audiosamples/phrase-ricky.wav', profiles)
#print(getMicrosoftOperationResult(statusUrl))
