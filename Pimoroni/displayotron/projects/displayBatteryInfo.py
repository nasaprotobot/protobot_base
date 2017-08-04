from ast import literal_eval as secureVal #Tuple parsing
from time import sleep #Wait 
import socket #Network connectivity
import threading #Multithreading
import os #Get IP, robot name
import dothat.backlight as backlight
import dothat.lcd as lcd
import serial

#Set up constants
BCAST_IP = "255.255.255.255"
ROBOT_ANNOUNCE_PORT = 55055
INSTRUCTIONS_PORT = 55056

#Get robot name
robotName = os.popen('hostname').read().split("\n")[0]

print("###===###===### ~~ " + robotName.upper() + " ACTIVATED ~~ ###===###===###")


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




lcd.clear()
lcd.write("Redy for combat!")

ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

if not ser.isOpen():         #Open the serial port
    ser.open()



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
        sleep(t)

#*****************************************************#
#                                                     #
# @returns the next unread line in the serial buffer  #
#                                                     #
#*****************************************************#
def read_next_line():
    
    line = ""
    c = ""
    while c != "\\n":   #terminate upon the newline character
        if c != "\\r":  #ignore the carriage return character
            line += c   #Concatenate with latest recieved  character
        c = (str(ser.read(1)).split("'"))[1] #retrieve only the incoming byte
    return line  #returns the now complete line of serial data


#*****************************************************#
#                                                     #
#    @returns the most recently transmitted line      #
#           *Clears the serial buffer*                #
#                                                     #
#*****************************************************#
def read_incoming_line():
    
    ser.flushInput()       #Empty the buffer
    read_next_line()       #read any leftover characters
    return read_next_line()#return the next line


#*****************************************************#
#                                                     #
#   This thread raises and lowers the led bargraph    #
#                                                     #
#*****************************************************#
class barThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            for i in range(0,100):      #Raise
                backlight.set_graph(i/100)
                sleep(.0025)
            
            for i in range(0,100):      #Lower
                backlight.set_graph((100-i)/100)
                sleep(.0025)



#*****************************************************#
#                                                     #
#   This thread sweeps a red bar accross the green    #
#                      bacground                      #
#                                                     #
#*****************************************************#

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
                
def mecanum_drive(dataDict):
    pwm1 = float(dataDict["axes"][0]) * 66 + 187
    pwm2 = float(dataDict["axes"][1]) * 66 + 187
    pwm3 = float(dataDict["axes"][2]) * 66 + 187
    
    ser.write(("[3," + str(pwm1) + "][9," + str(pwm2) + "][11," + str(pwm3) + "]").encode())
    
#barSweep = barThread(1, "bar", 1)
backSweep = backThread(2, "back", 2)

#barSweep.start()
backSweep.start()

#read_incoming_line()
###ANNOUNCE ROBOT PRESCENCE TO CONTROLLER
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
#Begin listening

while True:
    lcd.clear()                          #Clear the display and set cursor at [0,0]
##    val = 10#float(read_incoming_line())    #Read data from Arduino
##    lcd.write("Redy for combat!                Battery: " + str(val) + "V")  #Print the stuffs
##    backlight.set_graph((val - 6.5)/6.5) #Set bargraph to battery level
    #sleep(.25)                      #wait 1/4 seconds to allow serial buffer to catch up
    
    
    data = instructionSock.recv(1024) # buffer size is 1024 bytes
    data = data.decode('utf-8')
    data = data.split(",")
    dataDict = parseTelemetry(data)
    #if (dataDict["buttons"][0] == "1"):
    print("parsed: " + str(dataDict))
        
    mecanum_drive(dataDict)
    #print("received message: ") #+ data)
