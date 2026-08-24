# Hardware

## Bill of materials

- ESP32 dev board
- L298N dual H-bridge motor driver
- 2× geared DC motors, differential drive
- 5× IR reflectance sensors in a front-mounted array
- Buzzer (active low)
- 4×4 ArUco marker, id 100, mounted flat on top of the chassis
- Overhead USB camera on a stand covering the whole arena
- Checkerboard print (8×5 inner corners, 29 mm squares) for calibration

## Pin map

Defined at the top of `firmware/vanguard/vanguard.ino`.

| Function | GPIO |
| --- | --- |
| IR sensor 1 (far left) | 33 |
| IR sensor 2 | 32 |
| IR sensor 3 (centre) | 35 |
| IR sensor 4 | 34 |
| IR sensor 5 (far right) | 39 |
| Left motor IN1 / IN2 | 12 / 14 |
| Right motor IN1 / IN2 | 27 / 26 |
| Enable A / Enable B (PWM) | 13 / 25 |
| Buzzer | 15 |

GPIOs 34, 35 and 39 are input-only on the ESP32, which is fine for the sensors
but means they cannot be repurposed as outputs.

The buzzer is wired active-low: `digitalWrite(buzzer, LOW)` sounds it.

## Timing constants

These are the numbers that actually needed tuning on the physical arena, and
they will need retuning for a different surface, battery voltage or motor set.

| Constant | Value | What it does |
| --- | --- | --- |
| `leftSpeed` / `rightSpeed` | 255 | PWM duty on each motor |
| `nodeTurnDelay` | 660 ms | How long a turn at a node runs before line-following resumes |
| `turnDelay` | 20 ms | Correction pulse while centred on the line |
| `sideTurnDelay` | 60 ms | Correction pulse when an outer sensor catches a rail |

`nodeTurnDelay` is the sensitive one. Too short and the robot rejoins the line
before it has cleared the junction and immediately re-detects the same node; too
long and it overshoots past the next line. It was raised from 620 ms to 660 ms
late in the build after the drive batteries were changed.

## Camera calibration

The tracking maths needs the camera's intrinsics.

```bash
python vision/capture_calibration_images.py   # 's' to save a shot, 'q' to finish
python vision/calibration.py                  # writes data/calibration/MultiMatrix.npz
```

Twenty or so shots of the checkerboard at varied angles and distances is enough.
`vision/detect_markers.py` and `vision/marker_distance.py` are quick standalone
checks that the camera index is right and markers are being read cleanly.

All the vision scripts default to camera index 2; override with
`GEOGUIDE_CAMERA=0`.

## An approach that didn't work: PID line following

The line follower is a bang-bang controller — read the sensors, nudge left or
right for a fixed number of milliseconds. A PID controller was tried first,
deriving a position error from a weighted difference of the two inner sensors:

```cpp
int position = sensor2Value * 1.34 - sensor4Value * 1;
error = setPoint - position;
myPID.Compute();
out = map(output, 0, 255, -255, 255);

int leftSpeed = baseSpeed - out;
leftSpeed = map(leftSpeed, -255, 255, 0, 255);
int rightSpeed = baseSpeed + out;
rightSpeed = map(rightSpeed, -255, 255, 0, 255);
```

It was abandoned. Digital IR sensors give a three-level position signal, not the
continuous one a PID wants, so the derivative term was mostly noise and the
gains never generalised past a single arena section. The fixed-delay corrections
were less elegant but far more repeatable.

## Reference

`reference/qtr_sensor_library.pdf` — QTR reflectance sensor library
documentation, kept for the sensor characteristics and calibration notes.

Useful links:

- [Pololu QTR reflectance sensors](https://www.pololu.com/product/961) —
  [library source](https://pololu.github.io/qtr-sensors-arduino/_q_t_r_sensors_8cpp_source.html)
- [Pololu motor and driver docs](https://www.pololu.com/docs/0J18/16)
- [IR sensor module circuit](https://www.circuits-diy.com/ir-sensor-module-circuit/)
