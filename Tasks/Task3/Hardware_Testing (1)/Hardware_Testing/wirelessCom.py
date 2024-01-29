import socket
from time import sleep
import signal		
import sys		
from enum import Enum 

#globals
ip = "192.168.137.171"     

def signal_handler(sig, frame):
    print('Clean-up !')
    cleanup()
    sys.exit(0)

def cleanup():
    s.close()
    print("cleanup done")

def sendData(conn, addr, message) :
        conn.sendall(str.encode(str(message)))
        print("data sent", str.encode(str(message)))


path = ["SSRS", "RR", "SRSLSRSL"] 
emergency = 'e'

message = path[0]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, 8002))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("connected to {addr}".format(addr = addr))
        if (input("enter to send the first path   ")):
            sendData(conn, addr, path[0])
        
        while(True):
                
            mm = conn.recv(1024)
            mmm = mm.decode()
            print(mm)
            print(mmm)
            if(mmm == "ready"):
                if (input("enter a key to stop")):
                    sendData(conn, addr, emergency)
            elif (mmm == "send"):
                # if (input("enter a key to send a new path")):
                    sendData(conn, addr, path[1])


            

  


            
