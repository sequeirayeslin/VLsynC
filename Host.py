#!/usr/bin/env python
# coding: utf-8

# In[6]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:

try:
    import vlc
    vlc.MediaPlayer() #test
    noVlc = False
except:
    noVlc = True
import time
from pymongo import MongoClient
import PySimpleGUI as sg
from sys import argv
from datetime import datetime
import sys
import json

import ctypes
import platform

def make_dpi_aware():
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
make_dpi_aware()


my_new_theme = {'BACKGROUND': 'white',
                'TEXT': '#191919',
                'INPUT': '#d3d3d3',
                'TEXT_INPUT': '#191919',
                'SCROLL': '#c7e78b',
                'BUTTON': ('white', 'white'),
                'PROGRESS': ('#01826B', '#D0D0D0'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

sg.theme_add_new('mytheme', my_new_theme)
sg.theme('mytheme')

# modules needed: dnspython, python-vlc, pymongo, PySimpleGUI

### input data ###

mongoConnectionStr = "mongodb+srv://m001-student:m001-mongodb-basics@sandbox.8dtmz.mongodb.net/video?retryWrites=true&w=majority"
hostName = "Yeslin Sequeira"

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

def updateMongoInitData(sessionType, streamLink, movieName, audioTrack, disableSubs):
    db.partyHostData.update_one({"hostName":hostName}, {"$set":{"sessionType": sessionType, "streamLink": streamLink, "movieName":movieName, "audioTrack":audioTrack, "disableSubs": disableSubs}})

def updateMongo(mediaPlayer):
    playerTime = mediaPlayer.get_time()
    clockTime = getClkTime()
    playerState = str(mediaPlayer.get_state())
    
    try:
        db.partyHostData.update_one({"hostName":hostName}, {"$set":{"playerTime": playerTime, "clockTime": clockTime, "state":playerState}})
    except:
        pass
    

def getMillisecsFromTimeString(timeString):
    
    time_list = timeString.split(':')
    time_list = [float(elem) for elem in time_list]
    time_list = [elem * 60**power * 1000 for elem,power in zip(time_list, [2,1,0])]
    time_millisecs = sum(time_list)
    return int(time_millisecs)

def getGoTo(last_clock_time_string, last_player_time):
    
    last_clock_time_string = str(datetime.now().time())
    last_clock_time_millisecs = getMillisecsFromTimeString(last_clock_time_string)
    
    current_clock_time_string = str(datetime.now().time())
    current_clock_time_millisecs = getMillisecsFromTimeString(current_clock_time_string)
    
    goTo = last_player_time + (current_clock_time_millisecs - last_clock_time_millisecs)
    
    return goTo

def getTimeStringFromMillisecs(millisecs):
    
    secs = millisecs/1000
    temp = secs
    
    total_hours = int(temp/60/60)
    
    temp -= total_hours*60*60
    total_minutes = int(temp/60)
    
    temp -= total_minutes*60
    total_seconds = int(temp)
    
    return "{:02}:{:02}:{:02}".format(total_hours,total_minutes,total_seconds)
    
def get_video_length_string(mediaPlayer):

    video_lenght_in_millisecs = mediaPlayer.get_length()
    return getTimeStringFromMillisecs(video_lenght_in_millisecs)
    
def get_video_time_string(mediaPlayer):

    video_time_in_millisecs = mediaPlayer.get_time()
    return getTimeStringFromMillisecs(video_time_in_millisecs)
    
def wait_till_player_stable(mediaPlayer, window, extraDelay=0):
    video_state = str(mediaPlayer.get_state())
    while video_state != 'State.Paused' and video_state != 'State.Playing':
        video_state = str(mediaPlayer.get_state())
        window.read(timeout = 5) # keeps window from "not responding"
    time.sleep(extraDelay)
    return

def openWindow(name, layout, winType, eventMap=None, valueMap=None, scrSize=None):
    if winType == "eventMap":
        return openEventMapWindow(name, layout, eventMap)
    elif winType == "valueMap":
        return openValueReturnWindow(name, layout, valueMap)
    elif winType == "persistent":
        return openPersistentWindow(name, layout)
    elif winType == "persistentFullscreen":
        return openPersistentFullscreenWindow(name, layout, scrSize)
    
def openEventMapWindow(name, layout, eventMap):
    
    window = sg.Window(name , layout, font='Calibri', icon = 'Images/cool.ico', background_color="white", button_color="white", element_justification="center")
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            window.close()
            sys.exit()
        for event_in_dic in eventMap:
            if event == event_in_dic:
                window.close()
                return eventMap[event]

def openValueReturnWindow(name, layout, valueMap):
    
    window = sg.Window(name, layout, font='Calibri', icon = 'Images/cool.ico', button_color="white")
        
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            window.close()
            sys.exit()
        for event_in_dic in valueMap:
            if event == event_in_dic:
                window.close()
                return values[valueMap[event]]

def openPersistentWindow(name, layout):
    return sg.Window(name, layout, font='Calibri', element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], icon='Images/cool.ico', background_color="white", button_color="white")

def openPersistentFullscreenWindow(name, layout, scrSize):
    return sg.Window(name, layout, font='Calibri', element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], no_titlebar=True, location=(0,0), size=scrSize, keep_on_top=True)

def toggleFullscreen(mediaPlayer,playerWindow, playerWindowFullscreen, audioTrack, fullscreen, disableSubs):
    clockTime = getClkTime()
    playerTime = mediaPlayer.get_time()
    playerState = str(mediaPlayer.get_state())
    
    if fullscreen:
        playerToHide = playerWindowFullscreen
        playerToShow = playerWindow
    else:
        playerToHide = playerWindow
        playerToShow = playerWindowFullscreen
    
    playerToShow.un_hide()
    playerToHide.hide()
    playerToShow.force_focus()
    mediaPlayer.stop()
    mediaPlayer.play()
    wait_till_player_stable(mediaPlayer, playerToShow)
    goto = getGoTo(clockTime, playerTime)
    mediaPlayer.set_time(goto)
    if playerState == "State.Paused":
        mediaPlayer.pause()
    mediaPlayer.audio_set_track(audioTrack)
    if disableSubs:
        mediaPlayer.video_set_spu_delay(vidLen*1000)
    
    return ((not fullscreen), playerToShow)

### functions END ###

if __name__ == '__main__':

    # initializing a few variables
    sessionType = ""
    streamLink = "no_link"
    movieName = ""
    fullscreenMode = False
    audioTrack = 1
    
    with open("settings.json", "r") as audioSettingFile:
        settings = json.load(audioSettingFile)
        audioTrack = settings ["audioTrack"]
        disableSubs = settings ["disableSubs"]
    
    eventMap ={
        "Stream":"stream",
        "Local Sync":"local_file_sync"
    }
    
    #layouts of all windows in this program
    sessionTypeWindowLayout = [
        [sg.Text("What kind of session do you want?")],
        [sg.Button(key="Stream",image_filename='Images/stream.png', border_width = 0), sg.Button(key="Local Sync",image_filename='Images/localSync.png', border_width = 0)]
    ]

    streamLinkWindowLayout = [[sg.Input(key="-TEXT-", size=(25, 1)), sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]]

    browseWindowLayout = [[sg.Text("File"), sg.In(size=(25, 1), enable_events=True, key="-FILE-"), sg.Button(key="browse_button",target="-FILE-",button_type=sg.BUTTON_TYPE_BROWSE_FILE,border_width=0,image_filename = "Images/browse.png")]]

    enterMovieNameWindowLayout = [[sg.Input(key="-TEXT-", size=(25, 1)), sg.Button(key="Go",image_filename='Images/go.png', border_width = 0)]]

    playerLayout = [
        [sg.Image('', size=(900, 700), key='-VID_OUT-', pad = (0,0))],
        [sg.Text("00:00:00 / 00:00:00", key = 'playerPos'), sg.Slider(range=(1, 10000), orientation='h', size=(100, 10), key = "slider", disable_number_display = True, background_color="#c3c3c3", trough_color = "#c3c3c3", relief=sg.RELIEF_FLAT)],
        [sg.Button(key="Play",image_filename='Images/play.png', border_width = 0), sg.Button(key="Pause",image_filename='Images/pause.png', border_width = 0), sg.Button(key="Stop",image_filename='Images/stop.png', border_width = 0)]
    ]

    playerLayoutFullscreen =  [[sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))]]
    
    noVlcWindowLayout = [
        [sg.Text("You dont have VLC Media Player (64 bit version) installed!")],
        [sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]
    ]
    
    noNetworkWindowLayout = [
        [sg.Text("         No internet connection!         ")],
        [sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]
    ]
    
    if noVlc:
        openWindow("VLC Missing", noVlcWindowLayout, "eventMap", eventMap = {"OK":None})
        sys.exit()
    
    sessionType = openWindow("Session Type", sessionTypeWindowLayout, "eventMap", eventMap)
    
    if sessionType == "stream":
        
        video = openWindow("Enter Stream Link", streamLinkWindowLayout, "valueMap", valueMap = {"OK":"-TEXT-"})
        streamLink = video
                
    elif sessionType == "local_file_sync":
        # a check if script opened with a file
        if len(argv)>1:
            video = argv[1]
        else:
            # opens browse window if no file passed

            video = openWindow("Open File", browseWindowLayout, "valueMap", valueMap = {"-FILE-":"-FILE-"})
    

    movieName = openWindow("Enter Movie Name", enterMovieNameWindowLayout, "valueMap", valueMap = {"Go":"-TEXT-"})
    

    
    # a MongoClient class instance for connecting to MongoDB
    try:
        client = MongoClient(mongoConnectionStr)
        db = client.vlcSyncApp
        updateMongoInitData(sessionType, streamLink, movieName, audioTrack, disableSubs)
    except:
        openWindow("No Network", noNetworkWindowLayout, "eventMap", {"OK":None})
        sys.exit()

    # a database instance of vlcSyncApp database
    
    
    # opens player window
    #playerWindow = sg.Window("Player - {}".format(movieName), playerLayout, font='Calibri', element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], icon='Images/cool.ico', background_color="white", button_color="white")
    playerWindow = openWindow("Player - {}".format(movieName), playerLayout, "persistent")
    playerWindow['-VID_OUT-'].expand(True, True)
    
    scrSize = playerWindow.get_screen_dimensions()
    
    # creates fullscreen player window (to be hidden until called upon)
    #playerWindowFullscreen = sg.Window("Player", playerLayoutFullscreen, font='Calibri', element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], no_titlebar=True, location=(0,0), size=scrSize, keep_on_top=True)
    playerWindowFullscreen = openWindow("Player", playerLayoutFullscreen, "persistentFullscreen", scrSize = scrSize)
    playerWindowFullscreen['-VID_OUT-'].expand(True, True)
    playerWindowFullscreen.hide()
    
    #create media and media player instances
    mediaPlayer = vlc.MediaPlayer()
    mediaPlayer.set_hwnd(playerWindow['-VID_OUT-'].Widget.winfo_id())
    media = vlc.Media(video)
    mediaPlayer.set_media(media)
    mediaPlayer.get_instance().log_unset()
    mediaPlayer.play()
    
    wait_till_player_stable(mediaPlayer, playerWindow)
    
    vidLen = mediaPlayer.get_length()
    
    vidLen_str = get_video_length_string(mediaPlayer)
    
    mediaPlayer.audio_set_track(audioTrack)
    
    if disableSubs:
        mediaPlayer.video_set_spu_delay(vidLen*1000)
    
    activeWindow = playerWindow
    
    while True:

        updateMongo(mediaPlayer)
        
        for i in range(10):
            
            event, values = activeWindow.read(timeout = 1000)
            
            if event == "Play":
                mediaPlayer.play()
                wait_till_player_stable(mediaPlayer, activeWindow)
                updateMongo(mediaPlayer)
                
            elif event =="Pause":
                mediaPlayer.pause()
                wait_till_player_stable(mediaPlayer, activeWindow)
                updateMongo(mediaPlayer)
            
            elif event == "f":
                fullscreenMode, activeWindow = toggleFullscreen(mediaPlayer,playerWindow, playerWindowFullscreen, audioTrack, fullscreenMode, disableSubs)
                
            elif event == "Stop" or event == sg.WINDOW_CLOSED:
                db.partyHostData.update_one({"hostName":hostName}, {"$set":{"state":"State.Inactive"}})
                playerWindow.close()
                playerWindowFullscreen.close()
                mediaPlayer.stop()
                sys.exit()
               
            if not fullscreenMode:
                
                current_player_position = mediaPlayer.get_position()
                current_player_position_slider_scale = int(current_player_position * 10000)
                
                try:
                    
                    if values['slider'] < (current_player_position_slider_scale-50) or values['slider'] > (current_player_position_slider_scale+50):
                        goTo = values['slider']/10000
                        mediaPlayer.set_position(goTo)
                        wait_till_player_stable(mediaPlayer, playerWindow)
                        updateMongo(mediaPlayer)
                    else:
                        playerWindow['slider'].update(value=current_player_position_slider_scale)
                        
                    playerWindow['playerPos'].update(value = get_video_time_string(mediaPlayer)+' / '+vidLen_str)
                except:
                    playerWindow['slider'].update(value=current_player_position_slider_scale)
# %%
