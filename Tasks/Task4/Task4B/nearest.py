import cv2 as cv
from cv2 import aruco
import numpy as np
import csv

# load in the calibration data
calib_data_path = "MultiMatrix.npz"

calib_data = np.load(calib_data_path)
print(calib_data.files)

cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

MARKER_SIZE = 6  # centimeters (measure your printed marker size)

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

param_markers = aruco.DetectorParameters()

cap = cv.VideoCapture(0)

#######Read the lat_long.csv file#########
lat_lon ={}
count=1
csv_name = "lat_long.csv"
with open(csv_name,'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    print("Read function run")
    for row in csv_reader:
            id = row[0]
            print("No. of coordinates:",count)
            count= count + 1
            lat = row[1]
            lon = row[2]
            lat_lon[id]= [lat,lon]


def write_csv(loc, csv_name):

    # open csv (csv_name)
    # write column names "lat", "lon"
    # write loc ([lat, lon]) in respective columns

    '''

    ADD YOUR CODE HERE

    '''
    with open(csv_name,'w')as csv_file:
        csv_writer = csv.writer(csv_file,delimiter=',')
        csv_writer.writerow(['lat','lon'])
        csv_writer.writerow(loc)

def tracker(ar_id, lat_lon):

    # find the lat, lon associated with ar_id (aruco id)
    # write these lat, lon to "live_data.csv"

    '''

    ADD YOUR CODE HERE

    '''
    print("Tracker function has been called")
    coordinate = None
    ar_id = str(ar_id)
    if ar_id in lat_lon:
        coordinate = lat_lon[ar_id]
        with open("live.csv",'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['lat','lon'])
            csv_writer.writerow(coordinate)
    # also return coordinate ([lat, lon]) associated with respective ar_id.
    return coordinate











while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

    if marker_corners:

        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, MARKER_SIZE, cam_mat, dist_coef)
        total_markers = range(0, marker_IDs.size)

        # Find the index of the ArUco marker with ID '1'
        marker_1_index = np.where(marker_IDs == 1)[0]

        if len(marker_1_index) > 0:
            # Get the pose of the ArUco marker with ID '1'
            marker_1_pose = tVec[marker_1_index][0]

            # Initialize variables to store the ID and distance of the nearest marker
            nearest_marker_id = None
            nearest_marker_distance = float('inf')

            for ids, tVec_i in zip(marker_IDs, tVec):
                if not np.array_equal(ids, [1]):  # Skip the ArUco marker with ID '1'
                    # Calculate the distance to each other marker
                    distance = np.linalg.norm(marker_1_pose - tVec_i)

                    # Update the nearest marker information
                    if distance < nearest_marker_distance:
                        nearest_marker_id = ids[0]
                        
                        nearest_marker_distance = distance
                        

            # Display the ID and distance of the nearest marker to ArUco marker with ID '1'
            tracker(ids[0],lat_lon)
            print(f"Nearest marker to ArUco marker with ID '1': ID = {nearest_marker_id}, Distance = {round(nearest_marker_distance, 2)} units")

        for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):
            cv.polylines(frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA)
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

            # Calculating the distance
            distance = np.sqrt(tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2)

            # Draw the pose of the marker
            point = cv.drawFrameAxes(frame, cam_mat, dist_coef, rVec[i], tVec[i], 4, 4)
            #cv.putText(frame, f"Dist: {round(distance, 2)}", top_right, cv.FONT_HERSHEY_PLAIN, 1.3, (0, 0, 255), 2, cv.LINE_AA,)
            cv.putText(frame, f"{ids[0]},{round(distance, 2)}", top_right, cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv.LINE_AA,)
           # cv.putText(frame, f"x:{round(tVec[i][0][0],1)} y: {round(tVec[i][0][1],1)} ", bottom_right, cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 2, cv.LINE_AA,)
            
    cv.namedWindow('frame', cv.WINDOW_NORMAL)
    cv.resizeWindow('frame', 960, 1080)
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()
