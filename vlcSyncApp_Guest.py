import vlc
import time
from pymongo import MongoClient
import PySimpleGUI as sg
from sys import argv
from datetime import datetime
import sys


# modules needed: dnspython, python-vlc, pymongo, PySimpleGUI

### input data ###

mongoConnectionStr = #enter mongodb connection string here
hostName = "Your Name"

### input data END ###

###  In your mongodb server, create a database called 'vlcSyncApp' and a collection 'partyHostData', and add this doc to it:
###    {
###        "hostName": "Your Name",
###        "state": "State.Paused",
###        "clockTime": "00:00:00",
###        "playerTime": 0,
###        "movieName":"",
###        "sessionType":"local_file_sync",
###        "streamLink":"no_link"
###    }

### functions ###

def getHostData(hostName):
    return db.partyHostData.find_one({"hostName":hostName})

def syncToHost(hostStats):

    if hostStats['state'] == 'State.Paused' and str(mediaPlayer.get_state()) == 'State.Playing':
        mediaPlayer.pause()
        
    elif hostStats['state'] == 'State.Playing' and str(mediaPlayer.get_state()) == 'State.Paused':
        goTo = getGoTo(hostStats)
        mediaPlayer.set_time(goTo)
        mediaPlayer.play()
        
    elif hostStats['state'] == 'State.Playing':
        goTo = getGoTo(hostStats)
        playerTime = mediaPlayer.get_time()
        if playerTime <= goTo - 2000 or playerTime >= goTo + 2000:
            mediaPlayer.set_time(goTo)

def getGoTo(hostStats):
    
    last_clock_time_list = hostStats['clockTime'].split(':')
    last_clock_time_millisecs = sum( [int(float(item)*1000) * 60 ** i for i,item in zip(range(2,-1,-1), last_clock_time_list)] )
    
    current_clock_time_str = str(datetime.now().time())
    current_clock_time_list = current_clock_time_str.split(':')
    current_clock_time_millisecs = sum( [int(float(item)*1000) * 60 ** i for i,item in zip(range(2,-1,-1), current_clock_time_list)] )
    
    goTo = hostStats['playerTime'] + (current_clock_time_millisecs - last_clock_time_millisecs)
    
    return goTo
    
def get_video_length_string(mediaPlayer):

    video_lenght_in_millisecs = mediaPlayer.get_length()
    video_length_in_secs = video_lenght_in_millisecs/1000
    temp = video_length_in_secs
    
    total_hours = int(temp/60/60)
    
    temp -= total_hours*60*60
    total_minutes = int(temp/60)
    
    temp -= total_minutes*60
    total_seconds = int(temp)
    
    return "{:02}:{:02}:{:02}".format(total_hours,total_minutes,total_seconds)
    
def get_video_time_string(mediaPlayer):

    video_time_in_millisecs = mediaPlayer.get_time()
    video_time_in_secs = video_time_in_millisecs/1000
    temp = video_time_in_secs
    
    hours = int(temp/60/60)
    
    temp -= hours*60*60
    minutes = int(temp/60)
    
    temp -= minutes*60
    seconds = int(temp)
    
    return "{:02}:{:02}:{:02}".format(hours,minutes,seconds)
    
def wait_till_player_stable(mediaPlayer):
    vidLen = 0
    while vidLen == 0:
        vidLen = mediaPlayer.get_length()
    return

### functions END ###

if __name__=='__main__':

    #creating a MongoClient class instance for connecting to MongoDB
    client = MongoClient(mongoConnectionStr)

    # creating a database instance of vlcSyncApp database
    db = client.vlcSyncApp
    
    hostStats = getHostData(hostName)
    
    movieName = hostStats["movieName"]
    sessionType = hostStats["sessionType"]
    streamLink = hostStats["streamLink"]
    
    if sessionType == "stream":
        message1='"Streaming"'
        message2="You don't need to have the video file on your computer. "
    elif sessionType == "local_file_sync":
        if len(argv)>1:
            message1='"Local File Sync"'
            message2="Make sure you're using the same fileas your friends! "
        else:
            message1='"Local File Sync"'
            message2="You need to open a video file. Make sure you're using the same file as your friends! "
    
    #layouts of all windows in this program
    welcomeWindowLayout = [
        [sg.Text("{} is hosting {} for you in {} mode.\n{}\nAre you ready?".format(hostName, movieName, message1, message2) , text_color="#191919", background_color="white")],
        [sg.Button(key="Let's Go!",image_filename='Images/letsgo.png', border_width = 0)]
    ]
    
    browseWindowLayout = [[sg.Text("File", text_color="#191919", background_color="white"), sg.In(size=(25, 1), enable_events=True, key="-FILE-", text_color="#191919", background_color="#d3d3d3"), sg.Button(key="browse_button",target="-FILE-",button_type=sg.BUTTON_TYPE_BROWSE_FILE,border_width=0,image_filename = "Images/browse.png")]]

    errorWindowLayout = [[sg.Text("{}'s session is no longer active".format(hostName), text_color="#191919", background_color="white")],[sg.Button(key="OK", image_filename="Images/exit.png", border_width=0)]]
    
    playerLayout = [[sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))],
        [sg.Text("00:00:00 / 00:00:00", key = 'playerPos', background_color="white", text_color="#191919"), sg.Slider(range=(1, 10000), orientation='h', size=(100, 10), key = "slider", disable_number_display = True, background_color="#c3c3c3", trough_color = "#c3c3c3")]]
    
    playerLayoutFullscreen =  [[sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))]]
    
    if hostStats['state']=="State.Inactive":
        errorMessageWindow = sg.Window("Sorry!",errorWindowLayout, background_color="white", button_color="white", icon="Images/cool.ico",element_justification="center")
        while True:
            event, values = errorMessageWindow.read()
            if event == "OK" or event == sg.WINDOW_CLOSED:
                sys.exit()
    
    welcomeWindow = sg.Window("Hi there!", welcomeWindowLayout, element_justification='center', icon='Images/cool.ico', background_color="white", button_color="white")
    
    while True:
        event, values = welcomeWindow.read()
        if event == sg.WINDOW_CLOSED:
            sys.exit()
        elif event == "Let's Go!":
            break
    
    welcomeWindow.close()

    if sessionType == "stream":
        video = streamLink

    # Create file select window
    elif sessionType == "local_file_sync":
        if len(argv)>1:
            video = argv[1]
        else:
            browseWindow = sg.Window("Open File", browseWindowLayout, icon = 'Images/cool.ico', background_color="white", button_color="white",)
            while True:
                event, values = browseWindow.read()
                if event == sg.WINDOW_CLOSED:
                    sys.exit()
                elif event == "-FILE-":
                    video = values["-FILE-"]
                    break
            browseWindow.close()

    #create player window
    playerWindow = sg.Window("Player - {}".format(movieName), playerLayout, element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], icon='Images/cool.ico',background_color="white")
    playerWindow['-VID_OUT-'].expand(True, True)
    
    scrSize = playerWindow.get_screen_dimensions()
    
    #create fullscreen player window (to be hidden until called upon)
    playerWindowFullscreen = sg.Window("Player", playerLayoutFullscreen, element_justification='center', finalize=True, return_keyboard_events=True, margins=[0,0], no_titlebar=True, location=(0,0), size=scrSize, keep_on_top=True)
    playerWindowFullscreen['-VID_OUT-'].expand(True, True)
    playerWindowFullscreen.hide()
    
    #creating player and media instances and setting media to player
    mediaPlayer = vlc.MediaPlayer()
    media = vlc.Media(video)
    mediaPlayer.set_media(media)
    mediaPlayer.get_instance().log_unset()
    
    mediaPlayer.set_hwnd(playerWindow['-VID_OUT-'].Widget.winfo_id())
    mediaPlayer.play()
    
    wait_till_player_stable(mediaPlayer)
    
    vidLen = mediaPlayer.get_length()
    
    vidLen_str = get_video_length_string(mediaPlayer)
    
    hostStats = getHostData(hostName)
    goTo = getGoTo(hostStats)
    mediaPlayer.set_time(goTo)
    
    fullscreenMode = False
    
    while True:
        try:
            hostStats = getHostData(hostName)
        except:
            pass
            
        if hostStats['state'] == 'State.Inactive':
            playerWindow.close()
            playerWindowFullscreen.close()
            mediaPlayer.stop()
            errorMessageWindow = sg.Window("Sorry!",errorWindowLayout, background_color="white", button_color="white", icon="Images/cool.ico", element_justification="center")
            while True:
                event, values = errorMessageWindow.read()
                if event == "OK" or event == sg.WINDOW_CLOSED:
                    sys.exit()
            
        syncToHost(hostStats)
        
        for i in range(1):
        
            if fullscreenMode:
                activeWindow = playerWindowFullscreen
            else:
                activeWindow = playerWindow
                
            event, values = activeWindow.read(timeout = 1000)
            if event == "f":
                if not fullscreenMode:
                    playerWindow.hide()
                    playerWindowFullscreen.un_hide()
                    playerWindowFullscreen.force_focus()
                    mediaPlayer.stop()
                    mediaPlayer.set_hwnd(playerWindowFullscreen['-VID_OUT-'].Widget.winfo_id())
                    mediaPlayer.play()
                    wait_till_player_stable(mediaPlayer)
                    goto = getGoTo(hostStats)
                    mediaPlayer.set_time(goto)
                    if hostStats['state'] == "State.Paused":
                        mediaPlayer.pause()
                    fullscreenMode = True
                else:
                    playerWindow.un_hide()
                    playerWindowFullscreen.hide()
                    playerWindow.force_focus()
                    mediaPlayer.stop()
                    mediaPlayer.set_hwnd(playerWindow['-VID_OUT-'].Widget.winfo_id()) 
                    mediaPlayer.play()
                    wait_till_player_stable(mediaPlayer)
                    goto = getGoTo(hostStats)
                    mediaPlayer.set_time(goto)
                    if hostStats['state'] == "State.Paused":
                        mediaPlayer.pause()
                    fullscreenMode = False
                    
            elif event == sg.WINDOW_CLOSED:
                sys.exit()
                break
                
            curPos = (mediaPlayer.get_time()/vidLen)*10000
            curPos = int(curPos)
            playerWindow['slider'].update(value = curPos)
            curPos_str = get_video_time_string(mediaPlayer)
            playerWindow['playerPos'].update(value = curPos_str+' / '+vidLen_str)
