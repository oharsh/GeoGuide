# How it fits together

Three pieces cooperate: an ESP32 robot that can follow a line but has no idea
where it is, a laptop with an overhead camera that knows exactly where the robot
is but cannot steer it, and a socket between them.

```
      overhead camera
             │
             ▼
   ┌─────────────────────┐        TCP :8002        ┌──────────────────┐
   │   control_center    │ ──── route strings ───▶ │     Vanguard     │
   │      (laptop)       │ ◀─── status messages ── │     (ESP32)      │
   └─────────────────────┘                         └──────────────────┘
             │                                              │
             ▼                                        5× IR sensors
       live.csv → QGIS                                 2× DC motors
```

## Stage 1 — event detection

`control_center/event_detection.py` runs once, before the robot moves.

1. Grab a 1920×1080 frame of the arena and crop to the playing area.
2. Threshold on brightness and take contours. The printed event images are large
   bright rectangles; a size filter (90–200 px) keeps them and rejects both noise
   and the much smaller ArUco markers.
3. Crop each hit and push it through a fine-tuned InceptionV3 classifier, which
   returns one of five event classes (or blank for an empty location).
4. Events are found left to right, which maps onto arena locations A through E.
   Sort them by priority — Fire first, then Destroyed buildings, Humanitarian
   Aid, Military Vehicles, Combat — and pickle the result.

## Stage 2 — the mission

`control_center/control_center.py` runs three threads over one shared camera
frame.

**`grab_frames`** does nothing but keep the latest cropped frame in a global, so
the other two threads always look at the same view without fighting over the
capture device.

**`command_center`** is the state machine. It reads the event pickle, and walks
the locations in priority order. For each one it looks the route up in the
`ROUTES` table (`config.py`) and sends the string. Then it listens:

| Robot says | Meaning | Host does |
| --- | --- | --- |
| `ALERT` | I'm on the final approach to the destination | Watch my marker; reply `STOP` when I'm on the square |
| `SEND` | I've finished here, give me the next route | Send the next route, or the route home if none are left |
| `HOME` | I'm approaching the start box | Watch for the start square, reply `STOP` |

The robot never decides for itself that it has arrived. It just follows the line
and reports; the camera makes the call, comparing the robot's marker position
against the pixel coordinates in `STOPPING_POINTS` with a small tolerance.

**`track_robot`** produces the live map. Each frame it adaptive-thresholds the
image (much more robust than raw grayscale under uneven arena lighting), detects
every ArUco marker, and measures the distance from each to the robot's own
marker (id 100). The nearest marker within 80 px wins, and its latitude and
longitude — looked up in `lat_long.csv` — get written to `live.csv`, which QGIS
polls to animate the robot on a map.

A handful of extra markers are stuck to the arena away from the driving line,
listed as `STATIC_MARKERS`. Their positions never change, so they can be
hard-coded, and they fill in gaps where the line has no marker nearby — without
them the plotted position jumps.

## Stage 3 — the robot

`firmware/vanguard/vanguard.ino` is a three-state machine: `FOLLOW_LINE`,
`NODE_DETECT`, `STOP`.

Five IR sensors read the line. The middle three handle centring; the outer two
detect a node — the point where lines cross — which is what advances the route
string by one character. Each character is one instruction:

| Char | Meaning |
| --- | --- |
| `I` | Leaving the start box |
| `S` | Carry straight on through this node |
| `L` / `R` | Turn left / right at this node |
| `T` / `F` | End of leg; the two possible orientations the head can finish in |
| `Q` | Returning to the start box |

`T` and `F` exist because arriving at a location facing the wrong way makes the
next leg's turns come out mirrored. Encoding the finishing orientation in the
route string lets the host pre-compute the whole path rather than correcting
mid-run.

## Why the split

The robot has no odometry and no map. Putting all localisation on the camera
means the firmware stays a dumb line-follower — it never needs to know how far
it has travelled, only what to do at the next node — while the host handles
everything requiring a global view.
