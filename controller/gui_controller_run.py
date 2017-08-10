from appJar import gui #installed
import socket
import time
import collections
import threading
import pygame #came installed
import psutil #installed

BCAST_IP = "255.255.255.255"
ROBOT_HEARTBEAT_PORT = 55055
INSTRUCTIONS_PORT = 55056
HEARTBEAT_DISPLAY_TIMER = 2
VERSION = "0.8 (BETA)"

#Recieve robot heartbeats
def recieveLoop():
    while True:
        data, addr = heartbeatSock.recvfrom(1024)
        data = data.decode('utf-8').split(",")
        ip = addr[0]
        robotList[data[0]] = ip
        options[data[0]] = data[1:]

#Pump pygame events
def pump():
    while True:
        pygame.event.pump()
        time.sleep(0.01)

#Toggle fullscreen
def toggleFullscreen(button):
    if not app.exitFullscreen():
        app.setGeometry("fullscreen")

#Display controller information 
def displayStats():
    while True:
        app.setLabel("cpulabel", "CPU: " + str(psutil.cpu_percent()) + "%")
        time.sleep(1)
    
#Display robots and their configuration
def refreshRobots(button):
    global joystickSelection
    global optionSelection
    
    #Clear all information
    robotList.clear()
    joystickSelection.clear()
    optionSelection.clear()
    joysticks.clear()
    options.clear()
    
    #Wait for heartbeats to come in
    time.sleep(2)

    #Restore initial backend state
    joystickSelection = defaultJoysticks()
    optionSelection = defaultOptions()

    #This is just in case config was invalid before
    app.setListBoxState("robotchoices", "normal")
    app.setButtonState("gobutton", "normal")
    
    #If there are robots found
    if (len(robotList.keys()) > 0):
        #Update list of robots, select one
        app.updateListBox("robotchoices", robotList.keys(), select=True)
        app.setLabel("configlabel", "Configuration: Valid") #Safe to say it's valid because we're loading defaults
        refreshScreen("manual")
        
    #No robots found
    else:
        #Update list of robots, select one
        app.updateListBox("robotchoices", ["none"], select=True)
        app.setLabel("configlabel", "Configuration: n/a")
        refreshScreen("manual")

#Called when a new robot is selected. Display's that robot's configuration       
def refreshScreen(choiceGui):
    #Clear the visual elements
    clearProperties("Joystick(s)")
    clearProperties("Option(s)")

    active = app.getListItems("robotchoices")[0]

    #There is actually a robot available
    if (active != "none"):
        #Set visual elements to new values, callfunction set to False to not affect backend while we trigger visual state change
        app.setProperties("Joystick(s)", joystickSelection[active], callFunction = False)
        app.setProperties("Option(s)", optionSelection[active], callFunction = False)
        app.setPropertiesState("Joystick(s)", "normal")
        app.setPropertiesState("Option(s)", "normal")

    #There are no robots
    else:
        app.setProperties("Joystick(s)", { "none": True }, callFunction = False)
        app.setProperties("Option(s)", { "none": True }, callFunction = False)
        app.setPropertiesState("Joystick(s)", "disabled")
        app.setPropertiesState("Option(s)", "disabled")
        app.setButtonState("gobutton", "disabled")

#Return default value to be assigned to joystickSelection
def defaultJoysticks():

    #Dictionary we're returning
    compiled = collections.OrderedDict()

    #Call for joystick initialzation
    activateJoysticks()
    
    #For each robot
    for name in robotList.keys():

        #All robots have a none option
        compiled[name] = { "none": True }

        #Add all joysticks - False by default
        for joyname in joysticks.keys():
            compiled[name][joyname] = False

    #Return resulting list
    return compiled

#Return default value to be assigned to optionSelection
def defaultOptions():
    #Dictionary we're returning
    compiled = collections.OrderedDict()

    #For each robot
    for name in options.keys():
        #All robots have a none option
        compiled[name] = { "none": True }

        optionList = options[name]

        #Get reported options, set all to False by default
        for choice in optionList:
            compiled[name][choice] = False

    return compiled

def clearProperties(guiProp):
    for prop in app.getProperties(guiProp).keys():
        app.deleteProperty(guiProp, prop)

#Initialize all joysticks
def activateJoysticks():
    joysticks.clear()
    
    numJoy = pygame.joystick.get_count()
    for i in range(numJoy):

        #Get current joystick
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        joysticks[joystick.get_name().split(" ")[0]] = joystick

def updateBackend(propName):
    global joystickSelection
    global optionSelection

    app.setListBoxState("robotchoices", "normal")
    app.setButtonState("gobutton", "normal")
    app.setLabel("configlabel", "Configuration: Valid")
    
    selectedJoy = app.getProperties("Joystick(s)")
    joystickSelection[app.getListItems("robotchoices")[0]] = selectedJoy

    selectedOpt = app.getProperties("Option(s)")
    optionSelection[app.getListItems("robotchoices")[0]] = selectedOpt

    if not (True in selectedJoy.values()) or not (True in selectedOpt.values()):
        app.setListBoxState("robotchoices", "disabled")
        app.setButtonState("gobutton", "disabled")
        app.setLabel("configlabel", "Configuration: Invalid")
        
                      
#"Start the car"
def turnKey(button):
    global keyIn
    instT = threading.Thread(target=putInGear, daemon=True)

    if (keyIn == False):
        app.setButton("gobutton", "Starting...")

        #For each robot
        for robot, addr in robotList.items():

            #Ensure none is not checked for this robot
            if not (joystickSelection[robot]["none"]):

                hotSticks[addr] = []
                hotOptions[addr] = ""
                hotRobots.append(addr)
            
                #For each robot check their joystick selections
                for name, val in joystickSelection[robot].items():
                    
                    #If this joystick is selected
                    if (val == True):

                        #Append actual joystick object
                        stick = joysticks[name]
                        hotSticks[addr].append((stick, stick.get_name().split(" ")[0].lower(), stick.get_numaxes(),
                                                stick.get_numbuttons(), stick.get_numhats()))

                #Ensure none is not checked for this robot
                if not (optionSelection[robot]["none"]):
                    #Add options to transmission
                    for i in range(len(options[robot])):
                        hotOptions[addr] += "o{},{},".format(i,int(optionSelection[robot][options[robot][i]]))
                else:
                    #Add options to transmission
                    for i in range(len(options[robot])):
                        hotOptions[addr] += "o{},0,".format(i)

        app.setListBoxState("robotchoices", "disabled")
        app.setPropertiesState("Joystick(s)", "disabled")
        app.setPropertiesState("Option(s)", "disabled")
        app.setButtonBg("gobutton", "red")
        app.setButton("gobutton", "Stop")
        keyIn = True
        instT.start()

    else:
        keyIn = False
        hotSticks.clear()
        hotOptions.clear()
        hotRobots.clear()
        app.setListBoxState("robotchoices", "normal")
        app.setPropertiesState("Joystick(s)", "normal")
        app.setPropertiesState("Option(s)", "normal")
        app.setButton("gobutton", "Go")
        app.setButtonBg("gobutton", "green")
        time.sleep(0.1)

#"Drive the car"
def putInGear():
    j = 0
    while keyIn:

        #Cycle through all robots
        for addr in hotRobots:
            telemetry = ""
            joystickNum = 0
            
            #Start cycling through joysticks for this robot
            for joystickMeta in hotSticks[addr]:
                joystick = joystickMeta[0]
                
                #Add name of stick to transmission
                telemetry += "c{},{},".format(joystickNum, joystickMeta[1])
                joystickNum += 1

                #Get joystick info
                numAxes = joystickMeta[2]
                numButtons = joystickMeta[3]
                numHats = joystickMeta[4]

                #Collect controller state information
                for i in range( numAxes ):
                    axis = round(joystick.get_axis( i ), 3)
                    telemetry += "a{},{},".format(i, axis)

                for i in range( numButtons ):
                    button = joystick.get_button(i)
                    telemetry += "b{},{},".format(i, button)

                for i in range( numHats ):
                    hat = joystick.get_hat(i)
                    telemetry += "h{},{},".format(i, hat)

            telemetry += hotOptions[addr]          
            
            #All joysticks finished, cap transmission 
            telemetry += "endtrans"

            #Encode and send transmission
            MESSAGE = telemetry.encode('utf-8')
            instructionSock.sendto(MESSAGE, (addr, INSTRUCTIONS_PORT))

        #Send all robots back to back with no delay, then wait
        time.sleep(0.05)
        
    print("done")

def setupGUI():

    #Setup display basics
    app.setGeometry("fullscreen")
    app.showSplash("NASA Protobot Initiative", fill='blue', stripe='white', fg='black', font=44)
    app.setBg("grey")
    app.setFont(18)
    app.setStretch("column")
    app.setPadding([10,5])

    # add & configure widgets - widgets get a name, to help referencing them later
    app.addLabel("banner", "NASA Protobot Control Center", 0, 0, 3)
    app.setLabelBg("banner", "blue")
    app.setLabelFg("banner", "white")
    app.setLabelSticky("banner", "new")

    app.addLabel("versionlabel", "Version: " + VERSION, 1, 0)
    app.setLabelSticky("versionlabel", "ws")

    app.addLabel("batterylabel", "Battery: " + "69%", 2, 0)
    app.setLabelSticky("batterylabel", "ws")

    app.addLabel("connectionlabel", "Connection: " + "ONLINE", 3, 0)
    app.setLabelSticky("connectionlabel", "ws")

    app.addLabel("cpulabel", "CPU Usage: " + "20%", 4, 0)
    app.setLabelSticky("cpulabel", "ws")

    app.addLabel("configlabel", "Configuration: " + "Valid", 5, 0, 3)
    app.setLabelSticky("configlabel", "ws")

    app.addButton("fullscreentoggle", toggleFullscreen, 1, 2)
    app.setButton("fullscreentoggle", "Toggle Fullscreen")
    app.setButtonBg("fullscreentoggle", "DarkOliveGreen4")
    app.setButtonFg("fullscreentoggle", "white")
    app.setButtonSticky("fullscreentoggle", "wse")

    app.addButton("robotreturn", print("fix me!"), 2, 2)
    app.setButton("robotreturn", "Listen to Robot")
    app.setButtonBg("robotreturn", "DarkOliveGreen4")
    app.setButtonFg("robotreturn", "white")
    app.setButtonSticky("robotreturn", "wse")

    app.addLabel("robotprompt", "Select a robot:", 98, 0)
    app.setLabelBg("robotprompt", "grey")
    app.setLabelFg("robotprompt", "black")
    app.setLabelSticky("robotprompt", "sw")

    app.addListBox("robotchoices", robotList.keys(), 99, 0)
    app.setListBoxChangeFunction("robotchoices", refreshScreen)

    app.addProperties("Joystick(s)", joystickSelection["init"], 98, 1, 1, 2)
    app.setPropertiesSticky("Joystick(s)", "news")
    app.setPropertiesChangeFunction("Joystick(s)", updateBackend)

    app.addProperties("Option(s)", optionSelection["init"], 98, 2, 1, 2)
    app.setPropertiesSticky("Option(s)", "news")
    app.setPropertiesChangeFunction("Option(s)", updateBackend)

    app.addButton("gobutton", turnKey, 100, 2)
    app.setButton("gobutton", "Go")
    app.setButtonBg("gobutton", "green")
    app.setButtonFg("gobutton", "white")
    app.setButtonSticky("gobutton", "we")

    app.addButton("robotrefresh", refreshRobots, 100, 0)
    app.setButton("robotrefresh", "Find Robots")
    app.setButtonBg("robotrefresh", "snow3")
    app.setButtonSticky("robotrefresh", "we")


# ---------------------------------- MAIN PROGRAM ----------------------------------

#Non-constant globals - Keys are names
robotList = collections.OrderedDict()
joystickSelection = collections.OrderedDict()
optionSelection = collections.OrderedDict()
joysticks = collections.OrderedDict()
options = collections.OrderedDict()
hotSticks = collections.OrderedDict()
hotOptions = collections.OrderedDict()
joyMeta = collections.OrderedDict()
hotRobots = []

#Some basic initial values. User should never see these
robotList["init"] = "init"
joystickSelection["init"] = { "none": True, "init": False }
optionSelection["init"] = { "none": True, "init": False }

#Setup a socket for listening to robot heartbeats
heartbeatSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
heartbeatSock.bind(("", ROBOT_HEARTBEAT_PORT))

#Setup a robot heartbeat listener thread
heartbeatListenerThread = threading.Thread(target=recieveLoop,
                                   daemon=True) #Kill thread with rest of program

#Launch heartbeat thread
heartbeatListenerThread.start()

#Setup instruction broadcast socket
instructionSock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP

#"Key" is not in the ignition
keyIn = False

#Activate pygame
pygame.init()

#Initialize all joysticks
activateJoysticks()

#Setup a pump thread
pumpThread = threading.Thread(target=pump, daemon=True) #Kill thread with rest of program
pumpThread.start()

#Setup a stats thread. Can't be started until GUI is started
#statsThread = threading.Thread(target=displayStats, daemon=True)

#Start the GUI interface
app = gui("Protobot Control Center", "700x500")
setupGUI()
refreshRobots("setupcall")
#statsThread.start()
app.go()
pygame.quit()
