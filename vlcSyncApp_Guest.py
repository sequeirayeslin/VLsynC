import vlc
import time
from pymongo import MongoClient
import os

###  In your mongodb server, create a database called 'vlcSyncApp' and a collection 'partyHostData', and add this doc to it:
###    {
###        "hostName": "Your Name",
###        "state": "State.Paused",
###        "clockTime": "00:00:00",
###        "playerTime": 0
###    }

### input data ###

video = "test.mkv" # specify path to video
mongoConnectionStr = #enter your mongodb connection string here
hostName = "Your Name"

### input data END ###

os.environ['VLC_VERBOSE'] = '-2'

#creating a MongoClient class instance for connecting to MongoDB
client = MongoClient(mongoConnectionStr)

# creating a database instance of vlcSyncApp database
db = client.vlcSyncApp

#creating player and media instances and setting media to player
mediaPlayer = vlc.MediaPlayer()
media = vlc.Media(video)
mediaPlayer.set_media(media)

### functions ###

def getHostData(hostName):
    return db.partyHostData.find_one({"hostName":hostName})

def getGoTo(hostStats):
    clockTime = time.localtime()
    clockTime = time.strftime("%H:%M:%S", clockTime)
    clockTime = int(clockTime[0:2]) * 60 * 60 + int(clockTime[3:5]) * 60 + int(clockTime[6:8])
    hostClockTime = hostStats["clockTime"]
    hostClockTime = int(hostClockTime[0:2]) * 60 * 60 + int(hostClockTime[3:5]) * 60 + int(hostClockTime[6:8])
    
    hostPlayerTime = hostStats["playerTime"]
    goTo = hostPlayerTime + (clockTime - hostClockTime)*1000
    return goTo

def syncToHost(hostStats):

    if hostStats['state'] == 'State.Paused' and str(mediaPlayer.get_state()) == 'State.Playing':
        mediaPlayer.pause()
        print('\n\ncmd: pause\n')
        
    elif hostStats['state'] == 'State.Playing' and str(mediaPlayer.get_state()) == 'State.Paused':
        goTo = getGoTo(hostStats)
        mediaPlayer.set_time(goTo)
        mediaPlayer.play()
        print('\n\ncmd: play\n')
        
    elif hostStats['state'] == 'State.Playing':
        goTo = getGoTo(hostStats)
        playerTime = mediaPlayer.get_time()
        if playerTime <= goTo - 10000 or playerTime >= goTo + 10000:
            mediaPlayer.set_time(goTo)
            print('\n\ncmd: goto\n')
    

### functions END ###

print('''
{} loaded...
'''.format(video))

hostStats = getHostData(hostName)
goTo = getGoTo(hostStats)
mediaPlayer.play()
mediaPlayer.set_time(goTo)

while True:
    hostStats = getHostData(hostName)
    
    syncToHost(hostStats)
    
    currentPos = mediaPlayer.get_time()/1000
    hr = int(currentPos/60/60)
    currentPos -= hr*60*60
    min = int(currentPos/60)
    currentPos -= min*60
    sec = int(currentPos)
    
    print("Player Position: {}:{}:{}        \r".format(hr,min,sec), end = '')
    time.sleep(3)
