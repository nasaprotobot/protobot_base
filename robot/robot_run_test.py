#THIS FILE SHOULD BE RUNNING ON STARTUP WITH THE FOLLOWING IN rc.local
#python3 -u /home/pi/Documents/protobot_base/robot/robot_run.py > /home/pi/Documents/logs/robotlog.txt 2>&1 &

from ast import literal_eval as secureVal #Tuple parsing in parseTelemetry()
from time import sleep
import socket
import os
import sys
import threading
import smbus
import dothat.lcd as lcd
import dothat.backlight as backlight
import queue

BCAST_IP = "255.255.255.255"
ROBOT_ANNOUNCE_PORT = 55055
INSTRUCTIONS_PORT = 55056

bus = smbus.SMBus(1)

ARDUINO = 4

pause = False

dicts = queue.Queue(100)


### =====================================================================
### ============================= FUNCTIONS =============================
### =====================================================================

#Heartbeat function - used with thread
def broadcastLoop(sock, t, msg, dest, port):
    print("[OK] Heartbeat started!")
    while True:
        sock.sendto(msg, (dest, port))
        sleep(t)

#Watch for timeouts - used with thread
def timeoutWatchdog(timeoutTrigger):
    while not (timeoutTrigger[0]):
        timeoutTrigger[0] = True
        sleep(1)

    print("[ERROR] Timeout detected... restarting...")
    
    os.execv(sys.executable, ["python"] + sys.argv) #Restart the process

def backlightSweep():
    while True:
        for i in range(0,5):     #Forth          
            sleep(.025)
            backlight.single_rgb(i,255,0,0)#Center of sweeping bar

            for x in range(0,5):
                if x == i:
                    qsahsdkd = 7
                elif x+1 == i or x-1 == i:
                    backlight.single_rgb(x,128,128,0)
                else:
                    backlight.single_rgb(x,0,255,0)


        
        for i in range(0,5):  #and back
            sleep(.025)
            backlight.single_rgb(5-i,255,0,0)

            for x in range(0,5):
                if x == i:
                    bork = -7
                elif x+1 == i or x-1 == i:
                    backlight.single_rgb(5-x,128,128,0)
                else:
                    backlight.single_rgb(5-x,0,255,0)

#Parse the incoming telemetry
#into a usable data dictionary

#dataDict["logitech"]["axes"][0]
# c1,logitech,a0,123,a1,342,controller,saitek,a0,145,endtrans

def parseTelemetry(rawData):
    dataDict = { "axes": [], "buttons": [], "hats": [], "options": []}
    i = 0
    
    while (rawData[i] != "endtrans"):
        if (rawData[i][0] == "a"):
            dataDict["axes"].append(rawData[i+1])
        elif (rawData[i][0] == "b"):
            dataDict["buttons"].append(rawData[i+1])
        elif (rawData[i][0] == "o"):
            dataDict["options"].append(rawData[i+1])
        elif (rawData[i][0] == "h"):
            #Eval will treat the string as python code
            dataDict["hats"].append(secureVal(rawData[i+1] + ", " + rawData[i+2]))
            i += 1

        i += 2

    return dataDict
def parseTelemetryController(rawData):
    dataDict = {}
    dataDict["options"] = []

    i = 0
    while (rawData[i] != "endtrans"):
        if (rawData[i][0] == "c"):
            controller = rawData[i+1]
            dataDict[controller] = { "axes": [], "buttons": [], "hats": [], "options": []}

        if (rawData[i][0] == "a"):
            dataDict[controller]["axes"].append(rawData[i+1])
        elif (rawData[i][0] == "b"):
            dataDict[controller]["buttons"].append(rawData[i+1])
        elif (rawData[i][0] == "o"):
            dataDict["options"].append(rawData[i+1])
        elif (rawData[i][0] == "h"):
            #Eval will treat the string as python code
            dataDict[controller]["hats"].append(secureVal(rawData[i+1] + ", " + rawData[i+2]))
            i += 1

        i += 2        

    return dataDict

def doOptions(dataDict):
    global pause

    if dataDict["options"][0] == '1':
        #Add data to Queue
        dicts.put(dataDict)

        #Remove from queue and drive
##        print(dicts.qsize())
        if dicts.full():
            dataDict = dicts.get()
            pause = False
        else:
            pause = True
            
    if dataDict["options"][1] == '1':
        #Cut power in half
        for i in range(len(dataDict["logitech"]["axes"])):
            dataDict["logitech"]["axes"][i] = str(float(dataDict["logitech"]["axes"][i])/2)

    return dataDict
#Mecanum drive
def drive(dataDict):
    if pause:
        bus.write_i2c_block_data(ARDUINO, 0, [3,187,9,187,11,187])
        return
    
    pwm3 = int( -float(dataDict["logitech"]["axes"][0]) * 66 + 187)
    pwm9 = int( -float(dataDict["logitech"]["axes"][1]) * 66 + 187)
    pwm11 = int(-float(dataDict["logitech"]["axes"][2]) * 66 + 187)

    bus.write_i2c_block_data(ARDUINO, 0, [3, pwm3, 9, pwm9, 11, pwm11])

### ========================================================================
### ============================= MAIN PROGRAM =============================
### ========================================================================

#Welcome message
robotName = os.popen('hostname').read().split("\n")[0]
print("###===###===### ~~ " + robotName.upper() + " ACTIVATED ~~ ###===###===###")

#Check for a connection before proceeding
print("Checking for connection...")
waitToStart = True
while (waitToStart):
    waitToStart = False
    try:
        robotIP = os.popen('ip addr show wlan0').read().split("inet ")[1].split("/")[0]

    except IndexError:
        print("[WAIT] No connection detected... trying again...")
        waitToStart = True
        sleep(4)
        
print("[OK] Connection established!")


#ANNOUNCE ROBOT PRESCENCE TO CONTROLLER
#Socket setup
print("Preparing heartbeat socket...")
robotAnnounceSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
robotAnnounceSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
print("[OK] Heartbeat socket online!")

broadMessage = (robotName + ",5 sec delay,low power").encode('utf-8')
#Begin broadcasting on loop via another thread
print("Attempting to launch heartbeat thread...") #print confirm inside thread
announceThread = threading.Thread(target=broadcastLoop, args=
                                  (robotAnnounceSock, 1, broadMessage, BCAST_IP, ROBOT_ANNOUNCE_PORT,),
                                  daemon=True) #Kill this task when the main thread exits
announceThread.start()

###BEGIN LISTENING FOR INSTRUCTIONS
#Setup receiving port
print("Preparing instruction socket...")
instructionSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
instructionSock.bind(("", INSTRUCTIONS_PORT))
print("[OK] Instruction socket online")

print("Attempting to initialize pwm")
bus.write_i2c_block_data(ARDUINO, 0, [3,187,9,187,11,187])

print("All systems operational!")
print("NA.Sa, READY FOR COMBAT")
lcd.clear()
lcd.write("READY FOR COMBAT")
backlightThread = threading.Thread(target = backlightSweep, daemon = True)
backlightThread.start()

#Pause here until we start receiving data
instructionSock.recv(1024) # buffer size is 1024 bytes

#Begin watching for timeout
timeoutTrigger = [False]
timeoutThread = threading.Thread(target=timeoutWatchdog, args=
                                  (timeoutTrigger,),
                                  daemon=True) #Kill this task when the main thread exits
timeoutThread.start()




#This is what happens on every received instruction
while True:
    #Grab instruction from stack
    data = instructionSock.recv(1024)
    
    #Cancel impending timeout
    timeoutTrigger[0] = False

    #Organize data
    data = data.decode('utf-8')
    data = data.split(",")
    dataDict = parseTelemetryController(data) #parseTelemetry(data)
    dataDict = doOptions(dataDict)
    drive(dataDict)
        
    #sleep(.01)
    volts = bus.read_byte(ARDUINO)
    #print("val " + str(volts))
    volts = volts / 51 * 11
    lcd.clear()
    lcd.write("READY FOR COMBAT")
    lcd.write("Battery: ")
    lcd.write(str(round(volts,1)))
    lcd.write("V")
    backlight.set_graph((volts - 6)/6)
    
