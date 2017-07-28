from ast import literal_eval as secureVal #Tuple parsing
import socket
#import os
import time
import threading

#robotIP = os.popen('ip addr show wlan0').read().split("inet ")[1].split("/")[0]
#robotName = os.popen('hostname').read().split("\n")[0]

BCAST_IP = "255.255.255.255"
ROBOT_ANNOUNCE_PORT = 55055
INSTRUCTIONS_PORT = 55056
ANNOUNCE_MESSAGE = "hithere".encode('utf-8') #robotName.encode('utf-8')

#Parse the incoming telemetry into a usable data dictionary
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

#Heartbeat function - used with thread
def broadcastLoop(sock, t, msg, dest, port):
    while True:
        sock.sendto(msg, (dest, port))
        time.sleep(t)

###ANNOUNCE ROBOT PRESCENCE TO CONTROLLER
#Socket setup
robotAnnounceSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
robotAnnounceSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

#Begin broadcasting on loop via another thread
announceThread = threading.Thread(target=broadcastLoop, args=
                                  (robotAnnounceSock, 1, ANNOUNCE_MESSAGE, BCAST_IP, ROBOT_ANNOUNCE_PORT,),
                                  daemon=True) #Kill this task when the main thread exits
announceThread.start()

###BEGIN LISTENING FOR INSTRUCTIONS
#Setup receiving port
instructionSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
instructionSock.bind(("", INSTRUCTIONS_PORT))

print("All systems operational!")
print("NA.Sa, READY FOR COMBAT")
#Begin listening
while True:
    data = instructionSock.recv(1024) # buffer size is 1024 bytes
    data = data.decode('utf-8')
    data = data.split(",")
    dataDict = parseTelemetry(data)

    print("received message: ") #+ data)
    print("parsed: " + str(dataDict))
