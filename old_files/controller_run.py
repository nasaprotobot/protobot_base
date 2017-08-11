import socket
import time
import collections
import threading
import pygame
import tkinter

BCAST_IP = "255.255.255.255"
ROBOT_HEARTBEAT_PORT = 55055
INSTRUCTIONS_PORT = 55056
HEARTBEAT_DISPLAY_TIMER = 2

#Recieve robot heartbeats
def recieveLoop(robotList, heartbeatSock):
    while True:
        data, addr = heartbeatSock.recvfrom(1024)
        robotList[data.decode('utf-8')] = addr[0]

#Display robot heartbeats
def displayRobots(robotList):
    robotList.clear()
    print("Searching for robots...")
    time.sleep(2)
    i = 1
    print("Available robots: ")
    for name, ip in robotList.items():
        print(str(i) + ". " + name + " reporting in on: " + str(ip))
    print("------------------------------")    
    

#Setup a socket for robot heartbeats
heartbeatSock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
heartbeatSock.bind(("", ROBOT_HEARTBEAT_PORT))

#Dictionary of available robots
robotList = collections.OrderedDict()

#Setup a robot heartbeat listener thread
heartbeatListenerThread = threading.Thread(target=recieveLoop, args=
                                   (robotList, heartbeatSock,),
                                   daemon=True) #Kill thread with rest of program

#Setup a heartbeat display driver thread
heartbeatDisplayThread = threading.Thread(target=displayRobots, args=
                                   (robotList,),
                                   daemon=True) #Kill thread with rest of program

#Launch both heartbeat threads
heartbeatListenerThread.start()
heartbeatDisplayThread.start()



# ---------------------------------- MAIN PROGRAM ----------------------------------

#Prepare for user selection
time.sleep(5)
choice = -1
while choice > len(robotList) or choice <= 0:
    print("Select a robot: ")
    choice = input()
    choice = int(choice)

targetAddr = ""
targetAddr = list(robotList.values())[choice-1]

#Setup instruction broadcast socket
instructionSock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP

#Initialize the joysticks
pygame.init()

#Support for multi joysticks
numJoysticks = pygame.joystick.get_count()

while True:
    pygame.event.pump() #Pygame technicallity

    #Cycle through all joysticks
    for i in range( numJoysticks ):
        #Get current joystick
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        #Get joystick information
        numAxes = joystick.get_numaxes()
        numButtons = joystick.get_numbuttons()
        numHats = joystick.get_numhats()

        #Collect controller state information
        telemetry = ""
        for j in range( numAxes ):
            axis = round(joystick.get_axis( j ), 3)
            telemetry += "a{},{},".format(j, axis)

        for j in range( numButtons ):
            button = joystick.get_button(j)
            telemetry += "b{},{},".format(j, button)

        for j in range( numHats ):
            hat = joystick.get_hat(j)
            telemetry += "h{},{},".format(j, hat)

        #Cap transmission 
        telemetry += "endtrans"

        #Encode and send transmission
        MESSAGE = telemetry.encode('utf-8')
        instructionSock.sendto(MESSAGE, (targetAddr, INSTRUCTIONS_PORT))

    #Send all joysticks back to back with no delay, then wait
    time.sleep(0.05)


