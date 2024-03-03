
'''
* Team Id :          GG_1667
* Author List :      Abhishek Ranjan, Arijit Goswami, Gaurav Singh, Harsh Yadav 
* Filename:          ControlCenter.py
* Theme:             Geo Guide
* Functions:         calculate_distance(tuple, tuple), tracker(int, dict), take_frame(), signal_handler(),
*                    cleanup(), sendData(), liveTracking(), goto(), command_center(), track_bot(),
* Global Variables:  calculateDistance(tuple, tuple), tracker(), take_frame(), cleanup(),
                     sendData(), liveTracking(), goto(), command_center(), 
                     track_bot()
'''

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

#ip address of the host 
ip = "192.168.137.181" 


#Path variable
pickle_file = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/event/events.pickle"
csv_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/csvfiles/lat_long.csv"
csv_live = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/csvfiles/live.csv"

#Aruco parameters
MARKER_SIZE = 8   
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
param_markers = aruco.DetectorParameters()


#These point will be used to stop the bot 
stoppingPoints = {
    "A": (126, 381),
    "B": (325, 294),  
    "C": (325, 207),
    "D": (107, 197),
    "E": (110, 54),
    "Q": (34, 428),
}

#reading the lat_long.csv and copying it in the lat_lon dictionary
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

#event configuration is stored as a pickle file, here we are loading the pickle 
#file which was created by the EventDetection.py
test={}
with open(pickle_file, "rb") as f :
    test = pickle.load(f)
f.close()

#Here we assigning path to and from every event location on the arena
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

'''
* Function Name:     calulateDistance
* Input:             source --> coordinates of sorce 
*                    destination --> coordinates of destination
* Output:            distance between source and target
* Logic:             this function simply use basic maths to find distance between two points on the arena
* 
* Example Call:     calculateDistance(source, target)
'''
def calculateDistance(source, target):
  pos_x = pow(source[0] - target[0], 2)
  pos_y = pow(source[1] - target[1], 2)
  j = pow(pos_x + pos_y, 1/2)
  return int(j)

'''
* Function Name:     tracker
* Input:             ar_id   -> Id of the Aruco
*                    lat_lon -> dictionary containing latitude and longitude mapped to the Aruco Id.
* Output:            update the coordinates in the live.csv file
* Logic:             Write the coordinate associated with the Aruco id to the live.csv file
* 
* Example Call:     tracker(id[], lat_lon);
'''
def tracker(ar_id, lat_lon):
    coordinate = None
    ar_id = str(ar_id)
    if ar_id in lat_lon:
        coordinate = lat_lon[ar_id]
        with open(csv_live,'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['lat','lon'])
            csv_writer.writerow(coordinate)


'''
* Function Name:     take_frame
* Input:             None
* Output:            A global variable gframe
* Logic:             this function read frames from the cap object continuously in the 
*                    background and assign it to a global variable
* 
* Example Call:      take_frame();
'''
def take_frame():

    while True:
        ret, frame = cap.read()
        if ret:
            y=0
            x=75
            h=466
            w=466
            #use to crop the image
            frame = frame[y:y+h, x:x+w]

            global gframe
            gframe = frame        



'''
* Function Name:     sendData
* Input:             conn --> connection socket object
*                    addr --> address of the connection   
*                    message --> message to be transmitted
* Output:            None
* Logic:             this function send a message to the client at address 'addr' using a socket connection
* 
* Example Call:      sendData(conn, addr, message);
'''

def sendData(conn, addr, message) :
    #we need to encode the message before transmitting
    conn.sendall(str.encode(str(message)))

'''
* Function Name:     liveTracking
* Input:             None
* Output:            pos_x --> x coordinates of id 100
*                    pos_y --> y coordinates of id 100
* Logic:             liveTracking function find out the position of aruco id 100
* 
* Example Call:      liveTracking();
'''

def liveTracking():

  #defining aruco parameters
  marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
  param_markers = aruco.DetectorParameters()  
  while True:
    while True:
        #check for gframe
        if type(gframe) == np.ndarray:
            break
            
    frame = gframe

    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    #marker_corners: a tuple containing coordinates of detected aruco markers 
    #marker_IDs: array containing aruco id of the detected marker
    
    marker_corners, marker_IDs, _ = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)
      
    if marker_corners:
      for corners, id in zip(marker_corners, marker_IDs):
        if(id == 100):
          corners = corners.reshape(4, 2)
          #storing coordinates of corners of aruco id 100 
          top_right = corners[0].ravel()
          top_left = corners[1].ravel()
          bottom_right = corners[2].ravel()
          bottom_left = corners[3].ravel()

          #finding center of aruco id 100
          center_x = (top_right[0] + top_left[0]) / 2
          center_y = (top_right[1] + bottom_right[1]) / 2
          pos_x = int(center_x)
          pos_y = int(center_y)
          return (pos_x, pos_y)


'''
* Function Name:     goto
* Input:             current_pos -> vanguard current position
*                    destn_pos   -> vanguard next destination
*                    conn        -> conn socket object
*                    addr        -> address of the client
* Output:            Calls sendData function to send the path from current_pos to destn_pos
* Logic:             this function sends the path to the destination from a given current_pos
*                    it first check the current position and then based on that find the best 
*                    path to the destination
* Example Call:      goto('A', 'E', conn, addr);
'''
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


'''
* Function Name:     command_center
* Input:             None
* Output:            returns 1 if the robot reaches final destination
* Logic:             This is the main control center for the robot it manages several tasks, 
*                    it first find the destination from the test dictionary and uses a counter visited to
*                    keep track of number of destination already visited 
*                    It sends the path using sockets, it initializes a socket object which is used to  
*                    send data as well as receive data from the Vanguard.
*                    it uses custom messages to communicate to the Vanguard.
*                    ALERT: starts tracking aruco id 100 and sends a stop signal when vanguard reaches
*                    its destination
*                    SEND: when vanguard is ready to receive the next set of path to the destination
*                    HOME: when vanguard reaches home
*                    In order to stop the vanguard at the event location we are using stopping points 
*                    whenever vanguard comes in range of those stopping points a stop signal is sent
*                    
* Example Call:      command_center();
'''

def command_center():
    curr_pos = 'I' 
    visited = 0
    destination = list(test.keys())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, 8002))
        s.listen()
        print("...")
        conn, addr = s.accept()
        with conn:
            sleep(2)
            print("connected to {addr}".format(addr = addr))
            goto(curr_pos, destination[visited], conn, addr)
            curr_pos = destination[visited]
            visited +=1
            
            while(True):
                    
                enc_mes = conn.recv(1024)
                dec_mes = enc_mes.decode()
               
                if(dec_mes == "ALERT"):
                    while True:
                        live = liveTracking()
                        if (live[0] >= (stoppingPoints[curr_pos][0]-5) and live[0] <= (stoppingPoints[curr_pos][0]+5)):
                            if(live[1] >= (stoppingPoints[curr_pos][1]-5) and live[1] <= (stoppingPoints[curr_pos][1]+5)):
                                sendData(conn, addr, "STOP")
                                break
                        
                elif (dec_mes == "SEND"):
                    if visited<len(destination):
                        goto(curr_pos, destination[visited], conn, addr)
                        curr_pos = destination[visited]
                        visited +=1
                    else:
                        goto(curr_pos,'I', conn, addr)

                elif (dec_mes == "HOME"):
                    while True:
                        live = liveTracking()
                        # print(live)
                        if (live[0] >= (stoppingPoints["Q"][0]-10) and live[0] <= (stoppingPoints["Q"][0]+10)):
                            if(live[1] >= (stoppingPoints["Q"][1]-10) and live[1] <= (stoppingPoints["Q"][1]+10)):
                                sendData(conn, addr, "STOP")
                                print("MISSION COMPLETE")
                                return 1


'''
* Function Name:     track_bot
* Input:             None
* Output:            
* Logic:             Purpose of this function is to track the bot ie. vanguard continuously 
*                    and plot its coordinates on a live map in QGIS
*                    we have also used some extra aruco id which are not present on the arena in 
*                    order to increase the tracking of the vanguard.
*
* Example Call:      take_frame();
'''
def track_bot():
    
    aruco_coordinates = {}
    dist = {}

    aruco_coordinates[70] = (227, 339)
    aruco_coordinates[71] = (229, 290)
    aruco_coordinates[72] = (249, 245)
    aruco_coordinates[73] = (105, 383)
    aruco_coordinates[74] = (101, 197) 
    aruco_coordinates[75] = (328, 205)
    aruco_coordinates[76] = (325, 291)

    while True:
        while True:
            try:
                if type(gframe) == np.ndarray:
                    break

            except Exception as e:
                print(e)
                continue
        frame = gframe

       
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #we are using adaptiveThresholding in order to increase the efficiency and accuracy
        threshold_image = cv.adaptiveThreshold(gray_frame, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        
        gray_frame = threshold_image
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

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
                #appending coordinates of each detected aruco markers to the aruco_coordinates dictionary
                aruco_coordinates[ids[0]] = (pos_x, pos_y)
               
                

            for i, cord in aruco_coordinates.items():
                if not i == 100:
                    if 100 in aruco_coordinates:
                        #finding distance of each aruco marker from aruco id 100
                        dist[i] = calculateDistance(cord, aruco_coordinates[100])

            #sorting aruco on the basis of distance
            dist = dict(sorted(dist.items(), key=lambda a:a[1]))
        if dist.keys():
            nearest_id_distance = list(dist.values())[0]
            #nearest_id: nearest id to the aruco id 100
            nearest_id = list(dist.keys())[0]
            if nearest_id < 100 and nearest_id_distance<80:
                #writing location in the live.csv file cooresponding to the nearest_aruco id 
                tracker(nearest_id, lat_lon)             
                    
        #Resizing the Window      
        cv.namedWindow('frame', cv.WINDOW_NORMAL)
        cv.resizeWindow('frame', 700, 700)
        cv.imshow('frame', frame)

        key = cv.waitKey(1)
        if key == ord("q"):
            break
    
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":

  global cap
  cap = cv.VideoCapture(2)

  #we are using threading module to run all the three function simultaneously 
  #they will be accessing the same global frame generated by function take_frame
  t1 = threading.Thread(target=take_frame)
  t2 = threading.Thread(target=command_center)
  t3 = threading.Thread(target=track_bot)

  t1.start()
  sleep(2)
  t3.start()
  t2.start()
