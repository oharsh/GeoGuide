# GeoGuide

An autonomous line-following robot that navigates a scale arena, identifies
disaster-response scenes printed at five locations, visits them in priority
order, and plots its own position on a live map as it goes.

The robot itself is deliberately simple — an ESP32 that follows a black line and
does what it's told at each junction. Everything that requires knowing where it
is happens on a laptop watching the arena through an overhead camera.

## How it works, briefly

1. **Detect the events.** A camera frame of the arena is thresholded and
   contoured to find the five printed images. Each is classified by a fine-tuned
   InceptionV3 model into one of five classes — fire, destroyed buildings,
   humanitarian aid, military vehicles, combat.
2. **Plan the route.** The locations are sorted by priority and the robot is
   sent a turn-by-turn string for each leg over a TCP socket.
3. **Follow and watch.** The robot follows the line and counts junctions. It
   never decides it has arrived — the overhead camera tracks the ArUco marker on
   its roof and sends `STOP` when it's on the target square.
4. **Map it.** Every frame, the marker nearest the robot is looked up in a
   coordinate table and written to a CSV that QGIS polls, animating the robot on
   a georeferenced map of the arena.

[docs/architecture.md](docs/architecture.md) has the full picture.

## Layout

```
control_center/    Host-side Python: event detection, mission control, tracking
  config.py          Paths, network, arena geometry, route table
  event_detection.py Classify what's at each arena location (run first)
  control_center.py  Run the mission and drive the live map
firmware/
  vanguard/        ESP32 line-follower firmware
  hardware_tests/  Bench sketches for the WiFi link and the motor/IR wiring
vision/            Camera calibration and standalone ArUco utilities
training/          Fine-tune the event classifier
tools/             Interactive socket test for the host↔robot link
data/              Calibration matrix, datasets, QGIS layers, eval sets
docs/              Architecture, hardware, references
models/            Trained weights (not tracked — see models/README.md)
```

## Setup

```bash
conda env create -f environment.yml
conda activate geoguide
```

Before the first run you need three things that aren't in the repo:

| What | Where it goes | How to get it |
| --- | --- | --- |
| Trained weights | `models/object_classification.h5` | [models/README.md](models/README.md) |
| Marker coordinates | `data/qgis/lat_long.csv` | [data/qgis/README.md](data/qgis/README.md) |
| WiFi credentials | `firmware/vanguard/secrets.h` | Copy `secrets.example.h` and fill it in |

Then calibrate the overhead camera — see
[docs/hardware.md](docs/hardware.md#camera-calibration).

## Running

Flash `firmware/vanguard/vanguard.ino` to the ESP32, then on the host:

```bash
# 1. Identify what's at each arena location. Press 'q' to take the snapshot.
python control_center/event_detection.py

# 2. Run the mission. Waits for the robot to connect, then drives it.
python control_center/control_center.py
```

Both scripts default to camera index 2 and host IP `192.168.137.181`. Override
with environment variables rather than editing the source:

```bash
GEOGUIDE_CAMERA=0 GEOGUIDE_HOST_IP=192.168.1.20 python control_center/control_center.py
```

Everything else configurable — arena crops, stopping-point coordinates, the
route table — lives in `control_center/config.py`.

## Tuning notes

The arena coordinates in `config.py` (`STOPPING_POINTS`, `STATIC_MARKERS`) are
pixel positions in the cropped camera frame. They are specific to one camera
mount and will need re-measuring if the camera moves. The firmware's turn
delays are likewise tuned to one set of motors and batteries —
[docs/hardware.md](docs/hardware.md#timing-constants) explains what each one
does and which one to reach for first.

