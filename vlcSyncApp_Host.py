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

###  in the empty txt file, command.txt, type out : 'play', 'pause' or 'goto min:sec', Eg. goto 122:53
###  then save
###  the program will read the command, run the command, clear the file


### input data ###

video = "test.mkv" # specify path to video
mongoConnectionStr = #enter your mongodb connection string here

### input data END ###



os.environ['VLC_VERBOSE'] = '-2'

#creating a MongoClient class instance for connecting to MongoDB
client = MongoClient(mongoConnectionStr)

# creating a database instance of vlcSyncApp database
db = client.vlcSyncApp

mediaPlayer = vlc.MediaPlayer()
media = vlc.Media(video)
mediaPlayer.set_media(media)

### functions ###

def getCmd(cmdFile):
    with open(cmdFile, 'r') as cmFile:
        cmd = cmFile.read()
    with open(cmdFile, 'w') as cmFile:
        cmFile.write('')
    return cmd

def runCmd(cmd):
    if cmd == 'play':
        mediaPlayer.play()
        print('\n\ncmd: play\n')
    elif cmd == 'pause':
        mediaPlayer.pause()
        print('\n\ncmd: pause\n')
    elif cmd[0:4] == 'goto':
        goto = cmd[5:].split(':')
        goto = ( int(goto[0])*60 + int(goto[1]) ) * 1000
        mediaPlayer.set_time(goto)
        print('\n\ncmd: goto\n')

def getClkTime():
    return time.strftime("%H:%M:%S", time.localtime())

def updateMongo(playerTime, clockTime, playerState):
    db.partyHostData.update_one({"hostName":"Yeslin Sequeira"}, {"$set":{"playerTime": playerTime, "clockTime": clockTime, "state":playerState}})

def printCurPos():
    currentPos = mediaPlayer.get_time()/1000
    hr = int(currentPos/60/60)
    
    currentPos -= hr*60*60
    min = int(currentPos/60)
    
    currentPos -= min*60
    sec = int(currentPos)
    
    print("Player Position: {}:{}:{}        \r".format(hr,min,sec), end = '')

### functions END ###

print('''
{} loaded...
'''.format(video))
mediaPlayer.play()

while True:

    resp = getCmd('command.txt')
    runCmd(resp)
    
    clockTime = getClkTime()
    playerTime = mediaPlayer.get_time()
    playerState = str(mediaPlayer.get_state())
    
    updateMongo(playerTime, clockTime, playerState)
    
    printCurPos()
    
    time.sleep(3)
    
