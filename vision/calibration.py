"""Compute the overhead camera's intrinsics from checkerboard photos.

Reads every image in ``runtime/calibration_images`` (captured by
``capture_calibration_images.py``), finds the checkerboard corners in each, and
writes the resulting camera matrix and distortion coefficients to
``data/calibration/MultiMatrix.npz`` -- the file the tracking scripts load.
"""

import os

import cv2 as cv
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Inner-corner count of the checkerboard, and the size of one square in mm.
CHESS_BOARD_DIM = (8, 5)
SQUARE_SIZE = 29

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

calib_data_path = os.path.join(ROOT_DIR, "data", "calibration")
image_dir_path = os.path.join(ROOT_DIR, "runtime", "calibration_images")

os.makedirs(calib_data_path, exist_ok=True)

# prepare object points, i.e. (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
obj_3D = np.zeros((CHESS_BOARD_DIM[0] * CHESS_BOARD_DIM[1], 3), np.float32)

obj_3D[:, :2] = np.mgrid[0 : CHESS_BOARD_DIM[0], 0 : CHESS_BOARD_DIM[1]].T.reshape(
    -1, 2
)
obj_3D *= SQUARE_SIZE

obj_points_3D = []
img_points_2D = []

files = os.listdir(image_dir_path)  
for file in files:
    print(file)
    imagePath = os.path.join(image_dir_path, file)
    image = cv.imread(imagePath)
    grayScale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(image, CHESS_BOARD_DIM, None)
    if ret == True:
        obj_points_3D.append(obj_3D)
        corners2 = cv.cornerSubPix(grayScale, corners, (3, 3), (-1, -1), criteria)
        img_points_2D.append(corners2)

        img = cv.drawChessboardCorners(image, CHESS_BOARD_DIM, corners2, ret)

cv.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    obj_points_3D, img_points_2D, grayScale.shape[::-1], None, None
)
print("calibrated")

np.savez(
    f"{calib_data_path}/MultiMatrix",
    camMatrix=mtx,
    distCoef=dist,
    rVector=rvecs,
    tVector=tvecs,
)

print("-------------------------------------------")

print("loading data stored using numpy savez function\n \n \n")

data = np.load(f"{calib_data_path}/MultiMatrix.npz")

camMatrix = data["camMatrix"]
distCof = data["distCoef"]
rVector = data["rVector"]
tVector = data["tVector"]

print("loaded calibration data successfully")