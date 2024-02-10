import cv2 as cv
from cv2 import aruco
import numpy as np
import csv
import math
import os

calib_data_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Environment/camCal/MultiMatrix.npz"

calib_data = np.load(calib_data_path)

cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

MARKER_SIZE = 8  # centimeters 

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

param_markers = aruco.DetectorParameters()

cap = cv.VideoCapture(2)



#####################Read the coordinates from latlong.csv file and write to live.csv#########
os.chdir("/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task4/Task4B/track")
lat_lon ={}
count=1
csv_name = "latlong.csv"
with open('latlong.csv') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
            id = row[0]
            count= count + 1
            lat = row[1]
            lon = row[2]
            lat_lon[id]= [lat,lon]


def write_csv(loc, csv_name):

    with open(csv_name,'w') as csv_file:
        csv_writer = csv.writer(csv_file,delimiter=',')
        csv_writer.writerow(['lat','lon'])
        csv_writer.writerow(loc)

def tracker(ar_id, lat_lon):

    coordinate = None
    ar_id = str(ar_id)
    if ar_id in lat_lon:
        coordinate = lat_lon[ar_id]
        with open("live.csv",'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['lat','lon'])
            csv_writer.writerow(coordinate)
    return coordinate


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


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)



def main():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

        # print(marker_IDs)

        if marker_corners:

            rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, MARKER_SIZE, cam_mat, dist_coef)
            total_markers = range(0, marker_IDs.size)

            # Find the index of the ArUco marker with ID '100'
            marker_1_index = np.where(marker_IDs == 100)[0]

            if len(marker_1_index) > 0:
                marker_1_pose = tVec[marker_1_index][0]

                nearest_marker_id = None
                nearest_marker_distance = float('inf')

                for ids, tVec_i in zip(marker_IDs, tVec):
                    # Skip the ArUco marker with ID '100'
                    if not np.array_equal(ids, [100]):  
                        # Calculate the distance to each other marker
                        distance = calculate_distance(marker_1_pose[0][0], marker_1_pose[0][1], tVec_i[0][0], tVec_i[0][1])

                        # Update the nearest marker information
                        if distance < nearest_marker_distance:
                            nearest_marker_id = ids[0]
                            
                            nearest_marker_distance = distance
                tracker(nearest_marker_id,lat_lon)
                
            for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):
            
                corners = corners.reshape(4, 2)
                corners = corners.astype(int)
                top_right = corners[0].ravel()
                top_left = corners[1].ravel()
                bottom_right = corners[2].ravel()
                bottom_left = corners[3].ravel()

                # Calculating the distance with only X and Y Coordinates
                distance = np.sqrt(  tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2 )
                #cv.putText(frame, f"{round(tVec[i][0][0],1)},{round(tVec[i][0][1],1)} ", bottom_right, cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 2, cv.LINE_AA,)
                
                    
                    

        ###Resizing the Window#######        
        cv.namedWindow('frame', cv.WINDOW_NORMAL)
        cv.resizeWindow('frame', 1080, 720)
        cv.imshow("frame", frame)
        key = cv.waitKey(1)
        if key == ord("q"):
            break
    
    cap.release()
    cv.destroyAllWindows()

# return print(pos_x, pos_y)
if __name__ == "__main__":
    main()
