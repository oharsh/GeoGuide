"""Shared configuration for the host-side control center.

Every path here is resolved relative to the repository root, so the project can
be cloned anywhere. Values that change between setups (host IP, camera index)
can be overridden with environment variables.
"""

import os
from pathlib import Path

# --- Paths -------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RUNTIME_DIR = ROOT_DIR / "runtime"

# Trained event classifier. Not tracked in git -- see models/README.md.
MODEL_PATH = Path(os.environ.get("GEOGUIDE_MODEL", ROOT_DIR / "models" / "object_classification.h5"))

# Camera intrinsics produced by vision/calibration.py.
CALIBRATION_PATH = DATA_DIR / "calibration" / "MultiMatrix.npz"

# Arena snapshots and cropped event images written during a run.
ARENA_DIR = RUNTIME_DIR / "arena"

# Event configuration handed from event_detection.py to control_center.py.
EVENTS_PICKLE = RUNTIME_DIR / "events.pickle"

# Static ArUco id -> (lat, lon) lookup, and the single-row file QGIS polls.
LAT_LON_CSV = DATA_DIR / "qgis" / "lat_long.csv"
LIVE_CSV = DATA_DIR / "qgis" / "live.csv"

# --- Network -----------------------------------------------------------------

# IP of this machine on the hotspot the robot joins. Must match `host` in
# firmware/vanguard/secrets.h.
HOST_IP = os.environ.get("GEOGUIDE_HOST_IP", "192.168.137.181")
HOST_PORT = int(os.environ.get("GEOGUIDE_HOST_PORT", 8002))

# --- Camera ------------------------------------------------------------------

CAMERA_INDEX = int(os.environ.get("GEOGUIDE_CAMERA", 2))

# Full-resolution capture used for event detection.
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1080

# Crop applied to the raw event-detection frame to isolate the arena: (x, y, w, h).
ARENA_CROP = (400, 0, 1050, 1050)

# Tighter crop applied to the live tracking feed: (x, y, w, h).
TRACKING_CROP = (75, 0, 466, 466)

# --- ArUco -------------------------------------------------------------------

# Marker glued to the top of the robot.
ROBOT_MARKER_ID = 100

# Printed marker edge length, in centimeters.
MARKER_SIZE = 8

# A marker must be within this many pixels of the robot to count as its position.
NEAREST_MARKER_MAX_DISTANCE = 80

# --- Arena layout ------------------------------------------------------------

# Pixel coordinates (in the tracking crop) where the robot must halt. "Q" is the
# start/finish square; A-E are the five event locations.
STOPPING_POINTS = {
    "A": (126, 381),
    "B": (325, 294),
    "C": (325, 207),
    "D": (107, 197),
    "E": (110, 54),
    "Q": (34, 428),
}

# Extra markers placed off the driving line to densify position lookups. Their
# pixel coordinates are known ahead of time and never move.
STATIC_MARKERS = {
    70: (227, 339),
    71: (229, 290),
    72: (249, 245),
    73: (105, 383),
    74: (101, 197),
    75: (328, 205),
    76: (325, 291),
}

# Turn-by-turn strings sent to the robot, keyed [from][to]. "I" is the start box.
# Each character is one instruction the firmware consumes at a node:
#   F/T - finish leg (head forward / turned), S - straight on, L/R - turn,
#   I - leave the start box, Q - return to the start box.
ROUTES = {
    "I": {"A": "IRF",     "B": "IRLRF",  "C": "ISSRSF", "D": "ISSRF",  "E": "ISSSSF"},
    "A": {"B": "FLRF",    "C": "FLSRF",  "D": "TRSRF",  "E": "TRSSSF", "I": "TLQ"},
    "B": {"A": "TLRT",    "C": "FLLT",   "D": "TRLT",   "E": "TSRSSF", "I": "TLRLQ"},
    "C": {"A": "TLSRT",   "B": "FRRT",   "D": "TST",    "E": "TSRSF",  "I": "TSLSSQ"},
    "D": {"A": "TLSLF",   "B": "FRLF",   "C": "FSF",    "E": "TRSF",   "I": "TLSSQ"},
    "E": {"A": "TSSSLF",  "B": "TSSLSF", "C": "TSLSF",  "D": "TSLF",   "I": "TSSSSQ"},
}

# Event classes the model can emit, ordered by the priority the robot visits
# them in. The blank entry is the "no event here" class.
EVENT_PRIORITY = [
    "Fire",
    "Destroyed buildings",
    "Humanitarian Aid and rehabilitation",
    "Military Vehicles",
    "Combat",
    " ",
]

# Model output index -> (short label drawn on screen, full event name).
EVENT_NAMES = [
    ("combat", "Combat"),
    ("humanitarian_aid", "Humanitarian Aid and rehabilitation"),
    ("military_vehicles", "Military Vehicles"),
    ("fire", "Fire"),
    ("destroyed_buildings", "Destroyed buildings"),
    (" ", " "),
]
