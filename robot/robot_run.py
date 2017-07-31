#THIS FILE SHOULD BE RUNNING ON STARTUP WITH THE FOLLOWING IN rc.local
#python3 -u /home/pi/Documents/protobot_base/robot/robot_run.py > /home/pi/Documents/logs/robotlog.txt 2>&1 &

from ast import literal_eval as secureVal #Tuple parsing in parseTelemetry()
from time import sleep
import socket
import os
import threading

BCAST_IP = "255.255.255.255"
ROBOT_ANNOUNCE_PORT = 55055
INSTRUCTIONS_PORT = 55056


#Heartbeat function - used with thread
def broadcastLoop(sock, t, msg, dest, port):
    while True:
        sock.sendto(msg, (dest, port))
        sleep(t)

#Watch for timeouts - used with thread
def timeoutWatchdog(timeoutTrigger):
    while not (timeoutTrigger[0]):
        timeoutTrigger[0] = True
        sleep(1)

    print("Timeout detected... dying")
    os._exit(os.EX_UNAVAILABLE)
    
#Parse the incoming telemetry
#into a usable data dictionary
def parseTelemetry(rawData):
    dataDict = { "axes": [], "buttons": [], "hats": [] }
    i = 0
    while (rawData[i] != "endtrans"):
        if (rawData[i][0] == "a"):
            dataDict["axes"].append(rawData[i+1])
        elif (rawData[i][0] == "b"):
            dataDict["buttons"].append(rawData[i+1])
        elif (rawData[i][0] == "h"):
            #Eval will treat the string as python code
            dataDict["hats"].append(secureVal(rawData[i+1] + ", " + rawData[i+2]))
            i += 1

        i += 2

    return dataDict

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
        print("No connection detected... trying again...")
        waitToStart = True
        sleep(4)
        
print("Connection established!")


#ANNOUNCE ROBOT PRESCENCE TO CONTROLLER
#Socket setup
robotAnnounceSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
robotAnnounceSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

#Begin broadcasting on loop via another thread
announceThread = threading.Thread(target=broadcastLoop, args=
                                  (robotAnnounceSock, 1, robotName.encode('utf-8'), BCAST_IP, ROBOT_ANNOUNCE_PORT,),
                                  daemon=True) #Kill this task when the main thread exits
announceThread.start()

###BEGIN LISTENING FOR INSTRUCTIONS
#Setup receiving port
instructionSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
instructionSock.bind(("", INSTRUCTIONS_PORT))

print("All systems operational!")
print("NA.Sa, READY FOR COMBAT")

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
    dataDict = parseTelemetry(data)

    #TODO call drive method
