"""Capture the checkerboard photos that camera calibration is computed from.

Shows a live feed with the detected checkerboard overlaid. Press ``s`` to save
the current frame (only works while the board is detected) and ``q`` to finish.
Saved frames land in ``runtime/calibration_images``, where ``calibration.py``
picks them up. Twenty or so shots from varied angles gives a good result.
"""

import os

import cv2 as cv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMERA_INDEX = int(os.environ.get("GEOGUIDE_CAMERA", 2))

# Inner-corner count of the checkerboard being photographed.
Chess_Board_Dimensions = (8, 5)

n = 0  # saved image counter

image_path = os.path.join(ROOT_DIR, "runtime", "calibration_images")
os.makedirs(image_path, exist_ok=True)

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def detect_checker_board(image, grayImage, criteria, boardDimension):
    ret, corners = cv.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv.drawChessboardCorners(image, boardDimension, corners1, ret)

    return image, ret


cap = cv.VideoCapture(CAMERA_INDEX)

while True:
    _, frame = cap.read()
    copyFrame = frame.copy()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    image, board_detected = detect_checker_board(
        frame, gray, criteria, Chess_Board_Dimensions
    )
    cv.putText(
        frame,
        f"saved_img : {n}",
        (30, 40),
        cv.FONT_HERSHEY_PLAIN,
        1.4,
        (0, 255, 0),
        2,
        cv.LINE_AA,
    )

    cv.imshow("frame", frame)
    cv.imshow("copyFrame", copyFrame)

    key = cv.waitKey(1)

    if key == ord("q"):
        break
    if key == ord("s") and board_detected == True:
        
        cv.imwrite(f"{image_path}/image{n}.png", copyFrame)

        print(f"saved image number {n}")
        n += 1  
cap.release()
cv.destroyAllWindows()

print("Total saved Images:", n)
