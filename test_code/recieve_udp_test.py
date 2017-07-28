import socket


UDP_IP = "255.255.255.255"
UDP_PORT = 55055

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind(("", UDP_PORT))

print("entering... ")

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message:" + data.decode('utf-8'))
