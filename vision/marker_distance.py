"""Show every visible ArUco marker with its measured distance from the camera.

A standalone check that the camera calibration is good and the markers are
being picked up cleanly. Press ``q`` to quit.
"""

import os

import cv2 as cv
import numpy as np
from cv2 import aruco

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIB_DATA_PATH = os.path.join(ROOT_DIR, "data", "calibration", "MultiMatrix.npz")
CAMERA_INDEX = int(os.environ.get("GEOGUIDE_CAMERA", 2))

calib_data = np.load(CALIB_DATA_PATH)

cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

# Printed marker edge length, in centimeters.
MARKER_SIZE = 8

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

param_markers = aruco.DetectorParameters()

cap = cv.VideoCapture(CAMERA_INDEX)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

    if marker_corners:

        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, MARKER_SIZE, cam_mat, dist_coef)
        total_markers = range(0, marker_IDs.size)

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
            # cv.putText(frame, f"id: {ids[0]} Dist: {round(distance, 2)}", top_right, cv.FONT_HERSHEY_PLAIN, 1.3, (0, 0, 255), 2, cv.LINE_AA,)
            cv.putText(frame, f"{round(tVec[i][0][0],1)}, {round(tVec[i][0][1],1)} ", bottom_right, cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 2, cv.LINE_AA,)
            # print(ids, "  ", corners)
    cv.namedWindow('frame', cv.WINDOW_NORMAL)
    cv.resizeWindow('frame', 1080, 720)  
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()