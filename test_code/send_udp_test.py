import socket
import os

ipv4 = os.popen('ip addr show wlan0').read().split("inet ")[1].split("/")[0]

UDP_IP = "255.255.255.255"
UDP_PORT = 55055
MESSAGE = ("My name is not Cortana and I live at: " + ipv4).encode('utf-8')

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", MESSAGE.decode('utf-8'))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
