import socket
from time import sleep
import signal		
import sys		
from enum import Enum 

def signal_handler(sig, frame):
    print('Clean-up !')
    cleanup()
    sys.exit(0)

def cleanup():
    s.close()
    print("cleanup done")

ip = ""     #Enter IP address of laptop after connecting it to WIFI hotspot

class command(Enum):
    forward = 1
    stop = 0
    left = 2
    right = 4



#To undeerstand the working of the code, visit https://docs.python.org/3/library/socket.html
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 8002))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(100) #amount of data 
            print(counter)
            print(data)
            conn.sendall(str.encode(str(counter)))
            counter += 1
            sleep(1)
            if counter == 10:
                s.close()
                break
