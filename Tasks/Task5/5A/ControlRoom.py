import socket
from time import sleep
import signal		
import sys
import numpy as np
import cv2 as cv
from enum import Enum
import cv2.aruco as aruco
import pickle 
import threading
import math
import os
from cv2 import aruco
import csv

#globals
ip = "192.168.137.181" 

##paths
pickle_file = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/event/events.pickle"
calib_data_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Environment/camCal/MultiMatrix.npz"
csv_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/csvfiles/lat_long.csv"
csv_live = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/csvfiles/live.csv"

##csvWriter dependencies
MARKER_SIZE = 8   
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
param_markers = aruco.DetectorParameters()


##stopping points
stoppingPoints = {
    "A": (197, 388),
    "B": (415, 295),  
    "C": (420, 207),
    "D": (196, 198),
    "E": (199, 57),
    "Q": (125, 432),
}

##copying csv file
lat_lon ={}
count=1
with open(csv_path) as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
            id = row[0]
            count= count + 1
            lat = row[1]
            lon = row[2]
            lat_lon[id]= [lat,lon]

#loadingpickle file
test={}
with open(pickle_file, "rb") as f :
    test = pickle.load(f)
f.close()


sent = 0

#Destination Dictionary
A = {
     "B": "FLRF",
     "C": "FLSRF",
     "D": "TRSRF", 
     "E": "TRSSSF", 
     'I': "TLQ"
    }

B = {
    "A": "TLRT", 
    "C": "FLLT", 
    "D": "TRLT",
    "E": "TSRSSF", 
    'I':"TLRLQ"
    }

C = {
    "A": "TLSRT", 
    "B": "FRRT", 
    "D": "TST", 
    "E": "TSRSF", 
    'I': "TSLSSQ"
    }

D = {
    "A": "TLSLF", 
    "B": "FRLF", 
    "C": "FSF", 
    "E": "TRSF", 
    'I': "TLSSQ"
    }

E = {
    "A": "TSSSLF", 
    "B": "TSSLSF", 
    "C": "TSLSF", 
    "D": "TSLF", 
    'I': "TSSSSQ"
    }

I = {
    "A": "IRF", 
    "B": "IRLRF", 
    "C": "ISSRSF", 
    "D": "ISSRF", 
    "E": "ISSSSF"
    }


def calculateDistance(source, target):
  pos_x = pow(source[0] - target[0], 2)
  pos_y = pow(source[1] - target[1], 2)
  j = pow(pos_x + pos_y, 1/2)
  return int(j)

def csvWriter(ar_id, lat_lon):
    coordinate = None
    ar_id = str(ar_id)
    if ar_id in lat_lon:
        coordinate = lat_lon[ar_id]
        with open(csv_live,'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['lat','lon'])
            csv_writer.writerow(coordinate)
    return coordinate


def take_frame():

    while True:
        ret, frame = cap.read()
        global gframe
        gframe = frame
        
def signal_handler(sig, frame):
    print('Clean-up !')
    cleanup()
    sys.exit(0)

def cleanup():
    s.close()
    print("cleanup done")

def sendData(conn, addr, message) :
    conn.sendall(str.encode(str(message)))
    # print("string sent", str.encode(str(message)))

def liveTracking():

  calib_data = np.load(calib_data_path)
  cam_matrix = calib_data["camMatrix"]
  dist_coef = calib_data["distCoef"]
  marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
  param_markers = aruco.DetectorParameters()
  while True:
    while True:
        if type(gframe) == np.ndarray:
            break
            
    frame = gframe
    
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

def command_center():
    curr_pos = 'I' 
    sent = 0
    destination = list(test.keys())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, 8002))
        s.listen()
        print("...")
        conn, addr = s.accept()
        with conn:
            sleep(3)
            print("connected to {addr}".format(addr = addr))
            goto(curr_pos, destination[sent],conn, addr)
            curr_pos = destination[sent]
            sent +=1
            
            while(True):
                    
                enc_mes = conn.recv(1024)
                dec_mes = enc_mes.decode()
                # print(dec_mes)
               
                if(dec_mes == "ALERT"):
                    while True:
                        live = liveTracking()
                        # print(type(live),"ready", live[0], live[1])
                        if (live[0] >= (stoppingPoints[curr_pos][0]-5) and live[0] <= (stoppingPoints[curr_pos][0]+5)):
                            if(live[1] >= (stoppingPoints[curr_pos][1]-5) and live[1] <= (stoppingPoints[curr_pos][1]+5)):
                                sendData(conn, addr, "stop")
                                break
                        
                elif (dec_mes == "SEND"):
                    if sent<len(destination):
                        goto(curr_pos, destination[sent], conn, addr)
                        curr_pos = destination[sent]
                        sent +=1
                    else:
                        goto(curr_pos,'I', conn, addr)

                elif (dec_mes == "HOME"):
                    while True:
                        live = liveTracking()
                        # print(live)
                        if (live[0] >= (stoppingPoints["Q"][0]-10) and live[0] <= (stoppingPoints["Q"][0]+10)):
                            if(live[1] >= (stoppingPoints["Q"][1]-10) and live[1] <= (stoppingPoints["Q"][1]+10)):
                                sendData(conn, addr, "stop")
                                print("mission complete")
                                return 1

def track_bot():
    #loading calibration data
    calib_data = np.load(calib_data_path)
    cam_mat = calib_data["camMatrix"]
    dist_coef = calib_data["distCoef"]
    r_vectors = calib_data["rVector"]
    t_vectors = calib_data["tVector"]

    coord = {}
    dist = {}



    while True:
        # global gframe
        while True:
            try:
                if type(gframe) == np.ndarray:
                    break

            except Exception as e:
                print(e)
                continue
        frame = gframe
       
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

        # print(marker_IDs)

        if marker_corners:

            for corners, ids, _ in zip(marker_corners, marker_IDs, reject):
      
                corners = corners.reshape(4, 2)
                corners = corners.astype(int)

                top_right = corners[0].ravel()
                top_left = corners[1].ravel()
                bottom_right = corners[2].ravel()
                bottom_left = corners[3].ravel()

                center_x = (top_right[0] + top_left[0]) / 2
                center_y = (top_right[1] + bottom_right[1]) / 2
                pos_x = int(center_x)
                pos_y = int(center_y)

                coord[ids[0]] = (pos_x, pos_y)

                # cv.putText(gframe, str(ids[0]), tuple(top_left), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)
            for i, cord in coord.items():
                if not i == 100:
                    if 100 in coord:
                        dist[i] = calculateDistance(cord, coord[100])
            sort_dist = sorted(dist, key= lambda a : dist[a])
            dist = {i:dist[i] for i in sort_dist }  
            # if [dist.keys()][0]:
            #     print(type([*dist.values()]))
            #     print([*dist.values()][0])
        # if [dist.keys()][0] and [*dist.values()][0] < 18:
        if [dist.keys()][0]:
            csvWriter(list(dist.keys())[0], lat_lon)             
                    
                    

        #Resizing the Window      
        cv.namedWindow('frame', cv.WINDOW_NORMAL)
        cv.resizeWindow('frame', 700, 700)
        cv.imshow("frame", frame)
        key = cv.waitKey(1)
        if key == ord("q"):
            break
    
    cap.release()
    cv.destroyAllWindows()

def read_frame(cap):
    ret, frame = cap.read()
    return frame

if __name__ == "__main__":

  global cap
  cap = cv.VideoCapture(2)
  t1 = threading.Thread(target=take_frame)
  t2 = threading.Thread(target=command_center)
  t3 = threading.Thread(target=track_bot)

  t1.start()
  sleep(1)
  t3.start()
  t2.start()
