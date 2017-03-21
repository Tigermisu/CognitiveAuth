import requests
from time import sleep

API_KEY = ''

def getProfilesFromMicrosoft():
    request = requests.get('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles',
                           headers = {
                               'Ocp-Apim-Subscription-Key': API_KEY
                           })

    if(request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return getProfilesFromMicrosoft()

    return request.json()


def createMicrosoftProfile():
    request = requests.post('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles',
                           headers={
                               'Ocp-Apim-Subscription-Key': API_KEY
                           },
                            data = {
                                "locale": "en-us"
                            })

    if (request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return createMicrosoftProfile()

    return request.json()['identificationProfileId']

def createMicrosoftEnrollment(profileID, audioFilePath):
    request = requests.post('https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles/%s/enroll' % profileID,
                            headers={
                                'Ocp-Apim-Subscription-Key': API_KEY
                            },
                            files = {
                                "file": open(audioFilePath, "rb")
                            })

    if (request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return createMicrosoftEnrollment(profileID, audioFilePath)

    return [request.status_code, request.headers]

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

    if (request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return identifySpeaker(audioFilePath, candidateIDs)

    return getMicrosoftOperationResult(request.headers['Operation-Location'])

def getMicrosoftOperationResult(requestUrl):
    request = requests.get(requestUrl,
                            headers={
                                'Ocp-Apim-Subscription-Key': API_KEY
                            })

    json = request.json()

    if (request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return getMicrosoftOperationResult(requestUrl)

    try:
        if json['status'] == "notstarted" or json['status'] == "running":
            return getMicrosoftOperationResult(requestUrl)
        elif json['status'] == "failed":
            raise AssertionError("Failed to Execute Operation")
    except KeyError as e:
        print("Invalid key: %s" % e)
        print("Response: %s (%s)" % (request.text, request.status_code))

    return json

def deleteMicrosoftProfile(profileID):
    request = requests.delete(
        'https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles/%s' % profileID,
        headers={
            'Ocp-Apim-Subscription-Key': API_KEY
        })

    if (request.status_code == 429):
        print("Rate Limit Exceeded (Code %s)" % request.status_code)
        sleep(10)
        return deleteMicrosoftProfile(profileID)

    return request.status_code

def deleteAllProfiles():
    profiles = list(map(lambda x: x['identificationProfileId'], getProfilesFromMicrosoft()))
    for profile in profiles:
        deleteMicrosoftProfile(profile)


if __name__ == '__main__':
    #createMicrosoftProfile()
    #createMicrosoftEnrollment(createMicrosoftProfile(), "audiosamples/enrol-royo.wav")
    getProfilesFromMicrosoft()
    #createMicrosoftEnrollment("ac25bd0b-7340-43e3-ae81-662fe571ac14", "audiosamples/enrol-ricky.wav")
    #profiles = list(map(lambda x: x['identificationProfileId'], getProfilesFromMicrosoft()))
    #identifySpeaker('audiosamples/enrol-luis.wav', profiles)
    #statusUrl = identifySpeaker('audiosamples/phrase-ricky.wav', profiles)
    #print(getMicrosoftOperationResult(statusUrl))
