import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
	port='/dev/ttyUSB0', #The arduino is connected to a virtual serial port through its FTDI chip on the USB
	baudrate=9600,       #9600 bits per second
        parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS
)


if not ser.isOpen():         #Open the serial port
    ser.open()



#*****************************************************#
#                                                     #
# @returns the next unread line in the serial buffer  #
#                                                     #
#*****************************************************#
def read_next_line():
    line = ""
    c = ""
    while c != "\\n":
        if c != "\\r":
            line += c
        c = (str(ser.read(1)).split("'"))[1]
    return line


#*****************************************************#
#                                                     #
#    @returns the most recently transmitted line      #
#           *Clears the serial buffer*                #
#                                                     #
#*****************************************************#
def read_incoming_line():
    ser.flushInput()
    read_next_line()
    return read_next_line()

while True:
    print(read_next_line())

        

