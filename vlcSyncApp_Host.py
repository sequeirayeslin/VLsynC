import vlc
import time
from pymongo import MongoClient
import PySimpleGUI as sg
from sys import argv
from datetime import datetime
import sys

# modules needed: dnspython, python-vlc, pymongo, PySimpleGUI

### input data ###

mongoConnectionStr = #enter your mongodb connection string here
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

def getClkTime():
    return str(datetime.now().time())

def updateMongoInitData(sessionType, streamLink, movieName):
    db.partyHostData.update_one({"hostName":hostName}, {"$set":{"sessionType": sessionType, "streamLink": streamLink, "movieName":movieName}})

def updateMongo(player_time, clock_time, player_state):
    db.partyHostData.update_one({"hostName":hostName}, {"$set":{"playerTime": player_time, "clockTime": clock_time, "state":player_state}})

def getGoTo(last_clock_time_string, last_player_time):
    
    last_clock_time_list = last_clock_time_string.split(':')
    last_clock_time_millisecs = sum( [int(float(item)*1000) * 60 ** i for i,item in zip(range(2,-1,-1), last_clock_time_list)] )
    
    current_clock_time_string = str(datetime.now().time())
    current_clock_time_list = current_clock_time_string.split(':')
    current_clock_time_millisecs = sum( [int(float(item)*1000) * 60 ** i for i,item in zip(range(2,-1,-1), current_clock_time_list)] )
    
    goTo = last_player_time + (current_clock_time_millisecs - last_clock_time_millisecs)
    
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

if __name__ == '__main__':

    #layouts of all windows in this program
    sessionTypeWindowLayout = [
        [sg.Text("What kind of session do you want?" , text_color="#191919", background_color="white")],
        [sg.Button(key="Stream",image_filename='Images/stream.png', border_width = 0), sg.Button(key="Local Sync",image_filename='Images/localSync.png', border_width = 0)]
    ]

    streamLinkWindowLayout = [[sg.Input(key="-TEXT-", size=(25, 1), background_color="#d3d3d3", text_color="#191919"), sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]]

    browseWindowLayout = [[sg.Text("File", text_color="#191919", background_color="white"), sg.In(size=(25, 1), enable_events=True, key="-FILE-", background_color="#d3d3d3", text_color="#191919"), sg.Button(key="browse_button",target="-FILE-",button_type=sg.BUTTON_TYPE_BROWSE_FILE,border_width=0,image_filename = "Images/browse.png")]]

    enterMovieNameWindowLayout = [[sg.Input(key="-TEXT-", size=(25, 1), background_color="#d3d3d3", text_color="#191919"), sg.Button(key="Go",image_filename='Images/go.png', border_width = 0)]]

    playerLayout = [
        [sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))],
        [sg.Text("00:00:00 / 00:00:00", key = 'playerPos' , text_color="#191919", background_color="white"), sg.Slider(range=(1, 10000), orientation='h', size=(100, 10), key = "slider", disable_number_display = True, background_color="#c3c3c3", trough_color = "#c3c3c3", relief=sg.RELIEF_FLAT)],
        [sg.Button(key="Play",image_filename='Images/play.png', border_width = 0), sg.Button(key="Pause",image_filename='Images/pause.png', border_width = 0), sg.Button(key="Stop",image_filename='Images/stop.png', border_width = 0)]
    ]
    
    playerLayoutFullscreen =  [[sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))]]
    
    # initializing a few variables
    sessionType = ""
    streamLink = "no_link"
    movieName = ""
    
    sessionTypeWindow = sg.Window("Session Type", sessionTypeWindowLayout, icon = 'Images/cool.ico', background_color="white", button_color="white", element_justification="center")
    
    while True:
        event, values = sessionTypeWindow.read()
        if event == sg.WINDOW_CLOSED:
            sys.exit()
        elif event == "Stream":
            sessionType = "stream"
            break
        elif event == "Local Sync":
            sessionType = "local_file_sync"
            break
    sessionTypeWindow.close()
    
    if sessionType == "stream":
        streamLinkWindow = sg.Window("Enter Stream Link", streamLinkWindowLayout, icon = 'Images/cool.ico', background_color="white", button_color="white")
        
        while True:
            event, values = streamLinkWindow.read()
            if event == sg.WINDOW_CLOSED:
                sys.exit()
            elif event == "OK":
                streamLink = values["-TEXT-"]
                video = streamLink
                break
        streamLinkWindow.close()
                
    elif sessionType == "local_file_sync":
        # a check if script opened with a file
        if len(argv)>1:
            video = argv[1]
        else:
            # opens browse window if no file passed
            browseWindow = sg.Window("Open File", browseWindowLayout, icon = 'Images/cool.ico', background_color="white", button_color="white")
            while True:
                event, values = browseWindow.read()
                if event == sg.WINDOW_CLOSED:
                    sys.exit()
                elif event == "-FILE-":
                    video = values["-FILE-"]
                    browseWindow.close()
                    break
    
    enterMovieNameWindow = sg.Window("Enter Movie Name", enterMovieNameWindowLayout, icon = 'Images/cool.ico', background_color="white", button_color="white")
    
    while True:
        event, values = enterMovieNameWindow.read()
        if event == sg.WINDOW_CLOSED:
            sys.exit()
        elif event == "Go":
            movieName = values["-TEXT-"]
            break
    enterMovieNameWindow.close()
    

    
    # a MongoClient class instance for connecting to MongoDB
    client = MongoClient(mongoConnectionStr)

    # a database instance of vlcSyncApp database
    db = client.vlcSyncApp
    
    updateMongoInitData(sessionType, streamLink, movieName)
    
    # opens player window
    playerWindow = sg.Window("Player - {}".format(movieName), playerLayout, element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], icon='Images/cool.ico', background_color="white", button_color="white")
    playerWindow['-VID_OUT-'].expand(True, True)
    
    scrSize = playerWindow.get_screen_dimensions()
    
    # creates fullscreen player window (to be hidden until called upon)
    playerWindowFullscreen = sg.Window("Player", playerLayoutFullscreen, element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], no_titlebar=True, location=(0,0), size=scrSize, keep_on_top=True)
    playerWindowFullscreen['-VID_OUT-'].expand(True, True)
    playerWindowFullscreen.hide()
    
    #create meadia and meadia player instances
    mediaPlayer = vlc.MediaPlayer()
    mediaPlayer.set_hwnd(playerWindow['-VID_OUT-'].Widget.winfo_id())
    media = vlc.Media(video)
    mediaPlayer.set_media(media)
    mediaPlayer.get_instance().log_unset()
    mediaPlayer.play()
    
    wait_till_player_stable(mediaPlayer)
    
    vidLen = mediaPlayer.get_length()
    
    vidLen_str = get_video_length_string(mediaPlayer)
    
    fullscreenMode = False
    
    
    while True:

        playerTime = mediaPlayer.get_time()
        clockTime = getClkTime()
        playerState = str(mediaPlayer.get_state())
        
        try:
            updateMongo(playerTime, clockTime, playerState)
        except:
            pass
        
        for i in range(1):
            
            if fullscreenMode:
                activeWindow = playerWindowFullscreen
            else:
                activeWindow = playerWindow
            event, values = activeWindow.read(timeout = 1000)
            if event == "Play":
                mediaPlayer.play()
            elif event =="Pause":
                mediaPlayer.pause()
            elif event == "Stop" or event == sg.WINDOW_CLOSED:
                mediaPlayer.stop()
                db.partyHostData.update_one({"hostName":hostName}, {"$set":{"state":"State.Inactive"}})
                sys.exit()
            elif event == "f":
                if not fullscreenMode:
                    playerWindow.hide()
                    playerWindowFullscreen.un_hide()
                    playerWindowFullscreen.force_focus()
                    mediaPlayer.stop()
                    mediaPlayer.set_hwnd(playerWindowFullscreen['-VID_OUT-'].Widget.winfo_id())
                    mediaPlayer.play()
                    wait_till_player_stable(mediaPlayer)
                    goto = getGoTo(clockTime, playerTime)
                    mediaPlayer.set_time(goto)
                    if playerState == "State.Paused":
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
                    goto = getGoTo(clockTime, playerTime)
                    mediaPlayer.set_time(goto)
                    if playerState == "State.Paused":
                        mediaPlayer.pause()
                    fullscreenMode = False
            if not fullscreenMode:
                current_player_position = mediaPlayer.get_position()
                current_player_position_slider_scale = current_player_position * 10000
                current_player_position_slider_scale = int(current_player_position_slider_scale)
                try:
                    
                    if values['slider']< current_player_position_slider_scale-50 or values['slider']>current_player_position_slider_scale+50:
                        goTo = values['slider']/10000
                        mediaPlayer.set_position(goTo)
                    else:
                        playerWindow['slider'].update(value=current_player_position_slider_scale)
                        
                    playerWindow['playerPos'].update(value = get_video_time_string(mediaPlayer)+' / '+vidLen_str)
                except:
                    pass
