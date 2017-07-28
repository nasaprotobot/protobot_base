import time
import threading
import dothat.backlight as backlight
import dothat.lcd as lcd
import serial

lcd.clear()
lcd.write("Redy for combat!")

ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS
)

ser.isOpen()

def read_next_line():
    line = ""
    c = ""
    while c != "\\n":
        if c != "\\r":
            line += c
        c = (str(ser.read(1)).split("'"))[1]
    return line

def read_incoming_line():
    ser.flushInput()
    read_next_line()
    return read_next_line()

class barThread (threading.Thread): ##raise and lower the bargraph
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            for i in range(0,100):
                backlight.set_graph(i/100)
                time.sleep(.0025)
            
            for i in range(0,100):
                backlight.set_graph((100-i)/100)
                time.sleep(.0025)

class backThread (threading.Thread): #To sweep the led backlight
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        x = 0
        while True:
            for i in range(0,5):
                time.sleep(.025)
                backlight.single_rgb(i,255,0,0)

                for x in range(0,5):
                    if x == i:
                        qsahsdkd = 7
                    elif x+1 == i or x-1 == i:
                        backlight.single_rgb(x,128,128,0)
                    else:
                        backlight.single_rgb(x,0,255,0)
            for i in range(0,5):
                time.sleep(.025)
                backlight.single_rgb(5-i,255,0,0)

                for x in range(0,5):
                    if x == i:
                        bork = -7
                    elif x+1 == i or x-1 == i:
                        backlight.single_rgb(5-x,128,128,0)
                    else:
                        backlight.single_rgb(5-x,0,255,0)
                

#barSweep = barThread(1, "bar", 1)
backSweep = backThread(2, "back", 2)

#barSweep.start()
backSweep.start()

while True:
    val = float(read_incoming_line())
    lcd.clear()
    lcd.write(str(val))
    backlight.set_graph(val / 14)
    time.sleep(.25)