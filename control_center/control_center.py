"""Host-side mission controller.

Runs three threads against a single overhead camera feed:

* ``grab_frames``   -- keeps a shared latest frame from the camera.
* ``command_center``-- serves the robot over a TCP socket, handing it the route
                       to each event location in priority order and telling it
                       when to stop.
* ``track_robot``   -- watches the arena for ArUco markers, works out which
                       marker the robot is nearest to, and writes that marker's
                       latitude/longitude to a CSV that QGIS polls for a live map.

``event_detection.py`` must be run first: it produces the pickle of event
locations that this script reads to decide where to send the robot.
"""

import csv
import pickle
import socket
import threading
from time import sleep

import cv2 as cv
import numpy as np
from cv2 import aruco

import config

MARKER_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
DETECTOR_PARAMS = aruco.DetectorParameters()

# Latest frame from the camera, shared between all three threads.
gframe = None


def load_lat_lon():
    """Read the ArUco id -> [lat, lon] lookup table used for live plotting."""
    lat_lon = {}
    with open(config.LAT_LON_CSV) as csv_file:
        for row in csv.reader(csv_file):
            lat_lon[row[0]] = [row[1], row[2]]
    return lat_lon


def load_events():
    """Read the event configuration written by ``event_detection.py``."""
    with open(config.EVENTS_PICKLE, "rb") as f:
        return pickle.load(f)


def distance_between(source, target):
    """Straight-line pixel distance between two points on the arena."""
    return int(((source[0] - target[0]) ** 2 + (source[1] - target[1]) ** 2) ** 0.5)


def write_live_position(ar_id, lat_lon):
    """Write the coordinates mapped to ``ar_id`` into the live CSV QGIS reads."""
    ar_id = str(ar_id)
    if ar_id not in lat_lon:
        return
    with open(config.LIVE_CSV, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["lat", "lon"])
        csv_writer.writerow(lat_lon[ar_id])


def marker_center(corners):
    """Centre pixel of one detected marker, given its four corners."""
    corners = corners.reshape(4, 2)
    top_right, top_left, bottom_right = corners[0], corners[1], corners[2]
    center_x = (top_right[0] + top_left[0]) / 2
    center_y = (top_right[1] + bottom_right[1]) / 2
    return int(center_x), int(center_y)


def grab_frames(cap):
    """Continuously refresh the shared frame so every thread sees the same view."""
    global gframe
    x, y, w, h = config.TRACKING_CROP
    while True:
        ret, frame = cap.read()
        if ret:
            gframe = frame[y:y + h, x:x + w]


def send(conn, message):
    """Send a message to the robot. Everything on the wire is encoded text."""
    conn.sendall(str.encode(str(message)))


def robot_position():
    """Block until the robot's marker is visible, then return its pixel centre."""
    while True:
        while not isinstance(gframe, np.ndarray):
            pass

        gray_frame = cv.cvtColor(gframe, cv.COLOR_BGR2GRAY)
        marker_corners, marker_ids, _ = aruco.detectMarkers(
            gray_frame, MARKER_DICT, parameters=DETECTOR_PARAMS
        )
        if not marker_corners:
            continue

        for corners, marker_id in zip(marker_corners, marker_ids):
            if marker_id == config.ROBOT_MARKER_ID:
                return marker_center(corners)


def wait_until_reached(conn, point, tolerance):
    """Watch the robot approach ``point`` and send STOP once it is within range."""
    while True:
        pos_x, pos_y = robot_position()
        if abs(pos_x - point[0]) <= tolerance and abs(pos_y - point[1]) <= tolerance:
            send(conn, "STOP")
            return


def goto(current_pos, destination, conn):
    """Send the route from ``current_pos`` to ``destination``."""
    if current_pos != destination:
        send(conn, config.ROUTES[current_pos][destination])


def command_center():
    """Drive the mission: hand out routes, stop the robot, bring it home.

    Destinations come from the event pickle, already sorted by priority. The
    robot talks back with three messages:

    * ``ALERT`` -- it is closing on its destination; start watching for the
      stopping point and reply ``STOP`` when it is there.
    * ``SEND``  -- it is ready for the next route.
    * ``HOME``  -- it is on the final approach to the start box.
    """
    events = load_events()
    destinations = list(events.keys())
    curr_pos = "I"
    visited = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((config.HOST_IP, config.HOST_PORT))
        s.listen()
        print("waiting for the robot to connect...")
        conn, addr = s.accept()

        with conn:
            sleep(2)
            print("connected to {addr}".format(addr=addr))
            goto(curr_pos, destinations[visited], conn)
            curr_pos = destinations[visited]
            visited += 1

            while True:
                message = conn.recv(1024).decode()

                if message == "ALERT":
                    wait_until_reached(conn, config.STOPPING_POINTS[curr_pos], tolerance=5)

                elif message == "SEND":
                    if visited < len(destinations):
                        goto(curr_pos, destinations[visited], conn)
                        curr_pos = destinations[visited]
                        visited += 1
                    else:
                        goto(curr_pos, "I", conn)

                elif message == "HOME":
                    wait_until_reached(conn, config.STOPPING_POINTS["Q"], tolerance=10)
                    print("mission complete")
                    return


def track_robot(cap):
    """Plot the robot on a live QGIS map by snapping it to the nearest marker.

    The arena carries markers along the driving line; a handful of extra static
    markers fill the gaps where the line has none. Each frame we find every
    visible marker, measure how far each one is from the robot's own marker, and
    publish the coordinates of the closest.
    """
    lat_lon = load_lat_lon()
    marker_positions = dict(config.STATIC_MARKERS)
    distances = {}

    while True:
        while not isinstance(gframe, np.ndarray):
            pass
        frame = gframe

        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Adaptive thresholding picks markers out of uneven arena lighting far
        # more reliably than feeding the raw grayscale frame to the detector.
        gray_frame = cv.adaptiveThreshold(
            gray_frame, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
        )
        marker_corners, marker_ids, _ = aruco.detectMarkers(
            gray_frame, MARKER_DICT, parameters=DETECTOR_PARAMS
        )

        if marker_corners:
            for corners, ids in zip(marker_corners, marker_ids):
                marker_positions[ids[0]] = marker_center(corners)

            if config.ROBOT_MARKER_ID in marker_positions:
                robot = marker_positions[config.ROBOT_MARKER_ID]
                distances = {
                    marker_id: distance_between(pos, robot)
                    for marker_id, pos in marker_positions.items()
                    if marker_id != config.ROBOT_MARKER_ID
                }
                distances = dict(sorted(distances.items(), key=lambda a: a[1]))

        if distances:
            nearest_id, nearest_distance = next(iter(distances.items()))
            if nearest_id < config.ROBOT_MARKER_ID and nearest_distance < config.NEAREST_MARKER_MAX_DISTANCE:
                write_live_position(nearest_id, lat_lon)

        cv.namedWindow("arena", cv.WINDOW_NORMAL)
        cv.resizeWindow("arena", 700, 700)
        cv.imshow("arena", frame)

        if cv.waitKey(1) == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()


def main():
    cap = cv.VideoCapture(config.CAMERA_INDEX)

    # All three threads read the same shared frame produced by grab_frames.
    threading.Thread(target=grab_frames, args=(cap,), daemon=True).start()
    sleep(2)
    threading.Thread(target=track_robot, args=(cap,)).start()
    threading.Thread(target=command_center).start()


if __name__ == "__main__":
    main()
