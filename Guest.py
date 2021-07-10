try:
    import vlc
    vlc.MediaPlayer()
    noVlc = False
except:
    noVlc = True
import time
from pymongo import MongoClient
import PySimpleGUI as sg
from sys import argv
from datetime import datetime
import sys

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

mongoConnectionStr = #enter your mongodb connection string
hostName = #enter your name

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

def getHostData(hostName):
    return db.partyHostData.find_one({"hostName":hostName})

def syncToHost(hostStats):
    
    playerState = str(mediaPlayer.get_state())

    if hostStats['state'] == 'State.Paused' and playerState == 'State.Playing':
        mediaPlayer.pause()
        
    elif hostStats['state'] == 'State.Playing' and playerState == 'State.Paused':
        goTo = getGoTo(hostStats)
        mediaPlayer.set_time(goTo)
        mediaPlayer.play()
        
    elif hostStats['state'] == 'State.Playing':
        goTo = getGoTo(hostStats)
        playerTime = mediaPlayer.get_time()
        if playerTime <= goTo - 2000 or playerTime >= goTo + 2000:
            mediaPlayer.set_time(goTo)
            
def getMillisecsFromTimeString(timeString):
    
    time_list = timeString.split(':')
    time_list = [float(elem) for elem in time_list]
    time_list = [elem * 60**power * 1000 for elem,power in zip(time_list, [2,1,0])]
    time_millisecs = sum(time_list)
    return int(time_millisecs)

def getGoTo(hostStats):
    
    last_clock_time_millisecs = getMillisecsFromTimeString(hostStats['clockTime'])
    
    current_clock_time_millisecs = getMillisecsFromTimeString(getClkTime())
    
    goTo = hostStats['playerTime'] + (current_clock_time_millisecs - last_clock_time_millisecs)
    
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

def toggleFullscreen(mediaPlayer,playerWindow, playerWindowFullscreen, hostStats, audioTrack, fullscreen, disableSubs):

    pass
    '''if fullscreen:
        playerToHide = playerWindowFullscreen
        playerToShow = playerWindow
    else:
        playerToHide = playerWindow
        playerToShow = playerWindowFullscreen
    
    
    playerToShow.un_hide()
    playerToHide.hide()
    playerToShow.force_focus()
    mediaPlayer.stop()
    mediaPlayer.set_hwnd(playerToShow['-VID_OUT-'].Widget.winfo_id()) 
    mediaPlayer.play()
    wait_till_player_stable(mediaPlayer, playerToShow)
    goto = getGoTo(hostStats)
    mediaPlayer.set_time(goto)
    if hostStats["state"] == "State.Paused":
        mediaPlayer.pause()
    mediaPlayer.audio_set_track(audioTrack)
    if disableSubs:
        mediaPlayer.video_set_spu_delay(vidLen*1000)
    
    return ((not fullscreen), playerToShow)'''

### functions END ###

if __name__=='__main__':

    noNetworkWindowLayout = [
        [sg.Text("         No internet connection!         ")],
        [sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]
    ]
    
    fullscreenMode = False

    #creating a MongoClient class instance for connecting to MongoDB
    try:
        client = MongoClient(mongoConnectionStr)
        db = client.vlcSyncApp
        hostStats = getHostData(hostName)
    except:
        openWindow("No Network", noNetworkWindowLayout, "eventMap", {"OK":None})
        sys.exit()
    
    movieName = hostStats["movieName"]
    sessionType = hostStats["sessionType"]
    streamLink = hostStats["streamLink"]
    disableSubs = hostStats["disableSubs"]
    audioTrack = hostStats["audioTrack"]
    
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
        [sg.Text("{} is hosting {} for you in {} mode.\n{}\nAre you ready?".format(hostName, movieName, message1, message2))],
        [sg.Image("Images/watchingMovie.png", background_color="white")],
        [sg.Button(key="Let's Go!",image_filename='Images/letsgo.png', border_width = 0)]
    ]
    
    browseWindowLayout = [[sg.Text("File", text_color="#191919", background_color="white"), sg.In(size=(25, 1), enable_events=True, key="-FILE-", text_color="#191919", background_color="#d3d3d3"), sg.Button(key="browse_button",target="-FILE-",button_type=sg.BUTTON_TYPE_BROWSE_FILE,border_width=0,image_filename = "Images/browse.png")]]

    errorWindowLayout = [[sg.Text("{}'s session is no longer active".format(hostName), text_color="#191919", background_color="white")],[sg.Button(key="OK", image_filename="Images/exit.png", border_width=0)]]
    
    playerLayout = [[sg.Image('', size=(900, 700), key='-VID_OUT-', pad = (0,0))],
        [sg.Text("00:00:00 / 00:00:00", key = 'playerPos', background_color="white", text_color="#191919"), sg.Slider(range=(1, 10000), orientation='h', size=(100, 10), key = "slider", disable_number_display = True, background_color="#c3c3c3", trough_color = "#c3c3c3")]]
    
    #playerLayoutFullscreen =  [[sg.Image('', size=(900, 500), key='-VID_OUT-', pad = (0,0))]]
    
    noVlcWindowLayout = [
        [sg.Text("You dont have VLC Media Player (64 bit version) installed!")],
        [sg.Button(key="OK",image_filename='Images/ok.png', border_width = 0)]
    ]
    
    if noVlc:
        openWindow("VLC Missing", noVlcWindowLayout, "eventMap", eventMap = {"OK":None})
        sys.exit()
    
    if hostStats['state']=="State.Inactive":
        
        openWindow("Sorry!", errorWindowLayout, "eventMap", eventMap = {"OK":None})
        sys.exit()
        
    openWindow("Hi There!", welcomeWindowLayout, "eventMap", eventMap = {"Let's Go!":None})

    if sessionType == "stream":
        video = streamLink

    # Create file select window
    elif sessionType == "local_file_sync":
        if len(argv)>1:
            video = argv[1]
        else:
            video = openWindow("Open File", browseWindowLayout, "valueMap", valueMap = {"-FILE-":"-FILE-"})

    #create player window
    #playerWindow = sg.Window("Player - {}".format(movieName), playerLayout, font='Calibri', element_justification='center', finalize=True, resizable=True, return_keyboard_events=True, margins=[0,0], icon='Images/cool.ico')
    playerWindow = openWindow("Player - {}".format(movieName), playerLayout, "persistent")
    playerWindow['-VID_OUT-'].expand(True, True)
    
    #scrSize = playerWindow.get_screen_dimensions()
    
    #create fullscreen player window (to be hidden until called upon)
    #playerWindowFullscreen = sg.Window("Player", playerLayoutFullscreen, font='Calibri', element_justification='center', finalize=True, return_keyboard_events=True, margins=[0,0], no_titlebar=True, location=(0,0), size=scrSize, keep_on_top=True)
    #playerWindowFullscreen = openWindow("Player", playerLayoutFullscreen, "persistentFullscreen", scrSize = scrSize)
    #playerWindowFullscreen['-VID_OUT-'].expand(True, True)
    #playerWindowFullscreen.hide()
    
    #creating player and media instances and setting media to player
    mediaPlayer = vlc.MediaPlayer()
    mediaPlayer.set_hwnd(playerWindow['-VID_OUT-'].Widget.winfo_id())
    media = vlc.Media(video)
    mediaPlayer.set_media(media)
    mediaPlayer.get_instance().log_unset()
    mediaPlayer.play()
    
    wait_till_player_stable(mediaPlayer, playerWindow, extraDelay=3)
    
    vidLen = mediaPlayer.get_length()
    
    vidLen_str = get_video_length_string(mediaPlayer)
    
    
    mediaPlayer.audio_set_track(audioTrack)
    
    if disableSubs:
        mediaPlayer.video_set_spu_delay(vidLen*1000)
    
    #activeWindow = playerWindow
    
    hostStats = getHostData(hostName)
    goTo = getGoTo(hostStats)
    mediaPlayer.set_time(goTo)
    
    while True:
        try:
            hostStats = getHostData(hostName)
        except:
            pass
            
        if hostStats['state'] == 'State.Inactive':
            playerWindow.close()
            #playerWindowFullscreen.close()
            mediaPlayer.stop()
            openWindow("Sorry!", errorWindowLayout, "eventMap", eventMap = {"OK":None})
            sys.exit()
            
        syncToHost(hostStats)
        
        for i in range(1):
                
            event, values = playerWindow.read(timeout = 1000)
            '''if event == "f":
                fullscreenMode, activeWindow = toggleFullscreen(mediaPlayer,playerWindow, playerWindowFullscreen, hostStats, audioTrack, fullscreenMode, disableSubs)
                '''    
            if event == sg.WINDOW_CLOSED:
                playerWindow.close()
                playerWindowFullscreen.close()
                mediaPlayer.stop()
                sys.exit()
                break
                
            curPos = (mediaPlayer.get_time()/vidLen)*10000
            curPos = int(curPos)
            playerWindow['slider'].update(value = curPos)
            curPos_str = get_video_time_string(mediaPlayer)
            playerWindow['playerPos'].update(value = curPos_str+' / '+vidLen_str)
