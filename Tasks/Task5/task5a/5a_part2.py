import socket
from time import sleep
import signal		
import sys
import numpy as np
import cv2 as cv
from enum import Enum
import cv2.aruco as aruco

#globals
ip = "192.168.137.50" 
  
test = {"A":"Fire", "D":"Combat"}

sent = 0
emergency = 'e'



stoppingPoints = {
    "A": (197, 388),
    "B": (415, 295),  
    "C": (420, 207),
    "D": (195, 203),
    "E": (196, 58),
    "I": ()
}

#Destination Dictionary
A = {"B": "FLRF", "C": "FLSRF", "D": "TRSRF", "E": "TRSSSF", 'I':"TLI"}

B = {"A": "TLRT", "C": "FLLT", "D": "TRLT","E": "TSRSSF", 'I':"TLRLI"}

C = {"A": "TLSRT", "B": "FRRT", "D": "TST", "E": "TSRSF", 'I': "TLSRLI"}

D = {"A": "TLSLF", "B": "FRLF", "C": "FSF", "E": "TRSF", 'I': "TLSSI"}

E = {"A": "TSSSLF", "B": "TSSLSF", "C": "TSLSF", "D": "TSLF", 'I': "TSSSSI"}

I = {"A": "IRF", "B": "IRLRF", "C": "ISRLRF", "D": "ISSRF", "E": "ISSSSF"}

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

def liveTracking():
  calib_data_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Environment/camCal/MultiMatrix.npz"

  calib_data = np.load(calib_data_path)
  cam_matrix = calib_data["camMatrix"]
  dist_coef = calib_data["distCoef"]

  marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
  param_markers = aruco.DetectorParameters()

  cap = cv.VideoCapture(2)
  while True:
    ret, frame = cap.read()
    if not ret:
      break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)
      
    if marker_corners:
      for corners, id in zip(marker_corners, marker_IDs):
        if(id == 100):
          corners = corners.reshape(4, 2)
          # corners = corners.astype(int)
          top_right = corners[0].ravel()
          top_left = corners[1].ravel()
          bottom_right = corners[2].ravel()
          bottom_left = corners[3].ravel()

          center_x = (top_right[0] + top_left[0]) / 2
          center_y = (top_right[1] + bottom_right[1]) / 2
          # cv.circle(frame, (int(center_x), int(center_y)), 5, (0, 255, 0), -1)
          pos_x = int(center_x)
          pos_y = int(center_y)
          cap.release()
          return (pos_x, pos_y)


def goto(current_pos, destn_pos, conn, addr):
    if current_pos != destn_pos:
        if current_pos=='I':
            sendData(conn, addr, I[destn_pos])
        elif current_pos=="A":
            sendData(conn, addr, A[destn_pos])
        elif current_pos=="B":
                sendData(conn, addr, B[destn_pos])
        elif current_pos=="C":
                sendData(conn, addr, C[destn_pos])
        elif current_pos=="D":
                sendData(conn, addr, D[destn_pos])
        elif current_pos=="E":
                sendData(conn, addr, E[destn_pos])

def main():
    curr_pos = 'I' 
    sent = 0
    destination = list(test.keys())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, 8002))
        s.listen()
        print("........")
        conn, addr = s.accept()
        with conn:
            print("connected to {addr}".format(addr = addr))
            goto(curr_pos, destination[sent],conn, addr)
            curr_pos = destination[sent]
            sent +=1
            
            while(True):
                    
                mm = conn.recv(1024)
                mmm = mm.decode()
                print(mm)
                print(mmm)
                if(mmm == "ready"):
                    while True:
                        live = liveTracking()
                        print(type(live), live[0], live[1])
                        if (live[0] >= (stoppingPoints[curr_pos][0]-5) and live[0] <= (stoppingPoints[curr_pos][0]+5)):
                            if(live[1] >= (stoppingPoints[curr_pos][1]-5) and live[1] <= (stoppingPoints[curr_pos][1]+5)):
                                sendData(conn, addr, emergency)
                                break
                            else:
                                pass
                        else:
                            pass
                elif (mmm == "send"):

                    if sent<len(destination):
                        goto(curr_pos, destination[sent], conn, addr)
                        curr_pos = destination[sent]
                        sent +=1
                    else:
                        goto(curr_pos,'I', conn, addr)

if __name__ == "__main__":
  main()