import json
import APIBridge
import AudioRecorder
import datetime

from time import time
from sys import exit

users = {}
config = {}

def init():
    global users
    global config

    try:
        configFile = open("config.json")
        configRaw = configFile.read()
        configFile.close()
        config = json.loads(configRaw)
    except FileNotFoundError:
        print("ERROR: Configuration file 'config.json' not found.")
        exit(0)
    except json.decoder.JSONDecodeError as e:
        print("ERROR: Syntax error in configuration file '%s'." % e)
        exit(0)

    try:
        usersFile = open(config['database_file'])
        usersContent = usersFile.read()
        usersFile.close()
        users = json.loads(usersContent)
    except FileNotFoundError:
        print("ERROR: Database file '%s' not found." % config['database_file'])
        exit(0)
    except json.decoder.JSONDecodeError as e:
        print("ERROR: Syntax error in database file '%s'." % e)
        exit(0)
    except KeyError:
        print("ERROR: Configuration file is missing key 'database_file'")
        exit(0)
    except Exception as e:
        print("ERROR: %s" % e)
        exit(0)

    try:
        APIBridge.API_KEY = config['api_key']
    except KeyError:
        print("ERROR: Configuration file is missing key 'api_key'")
        exit(0)

def saveUsers():
    global users
    usersFile = open(config['database_file'], 'w')
    usersFile.write(json.dumps(users, sort_keys=True, indent=2))
    usersFile.close()

init()

def createUser(name):
    profileId = APIBridge.createMicrosoftProfile()
    users['users'][profileId] = {
        "id": profileId,
        "name": name,
        "access_count": 0,
        "enrolled": False,
        "last_access": "None"
    }

    saveUsers()

    return profileId

def enrollUser(id):
    filename = 'enrollments/%s.wav' % id
    print("Recording background noise.")
    AudioRecorder.record_to_file(filename)
    print("Done recording.")
    return enrollUserWithFile(id, filename)

def enrollUserWithFile(id, file):
    status = APIBridge.createMicrosoftEnrollment(id, file)
    print("File uploaded, awaiting processing. (Code %s)" % str(status[0]))
    status = APIBridge.getMicrosoftOperationResult(status[1]['Operation-Location'])
    print("User %s enrolled!" % id)
    users['users'][id]['enrolled'] = True
    saveUsers()

    return status

def identifyUser():
    filename = 'phrases/%s.wav' % str(time())
    print("Recording background noise.")
    AudioRecorder.record_to_file(filename)
    print("Done recording. Standby for identification.")
    return identifyUserWithFile(filename)

def identifyUserWithFile(filename):
    candidates = list(filter(lambda x: users['users'][x]['enrolled'], users['users'].keys()))
    result = APIBridge.identifySpeaker(filename, candidates)
    print(result)
    if result['processingResult']['identifiedProfileId'] == '00000000-0000-0000-0000-000000000000':
        return "Invalid audio sample or unknown speaker"
    elif result['processingResult']['confidence'] != 'High':
        return "Unable to be certain of the speaker's identity."
    else:
        speaker = users['users'][result['processingResult']['identifiedProfileId']]
        speaker['access_count'] += 1
        outputString = "Identified user as %s, this is their access #%s, last access: %s" \
                       % (speaker['name'], speaker['access_count'], speaker['last_access'])
        speaker['last_access'] = datetime.datetime.today().strftime("%A, %d. %B %Y %I:%M%p")
        saveUsers()
        return outputString

if __name__ == '__main__':
    """
    print("deleting all profiles")
    APIBridge.deleteAllProfiles()

    print("running tests")

    newId = createUser("Luis")
    enrollUserWithFile(newId, "audiosamples/enrol-luis.wav")

    newId = createUser("Chris")
    enrollUserWithFile(newId, "enrollments/72480cce-5c84-4332-8d3f-888a6fef679a.wav")

    newId = createUser("Pao")
    enrollUserWithFile(newId, "audiosamples/enrol-pao.wav")

    newId = createUser("Ricky")
    enrollUserWithFile(newId, "audiosamples/enrol-ricky.wav")

    newId = createUser("Royo")
    enrollUserWithFile(newId, "audiosamples/enrol-royo.wav")

    newId = createUser("Kendra")
    enrollUserWithFile(newId, "audiosamples/enrol-kendra.wav")

    print("Enrolled everyone!")

    print(users, APIBridge.getProfilesFromMicrosoft())
    """
    print(identifyUserWithFile("audiosamples/phrase-kendra.wav"))
    #print(identifyUser())