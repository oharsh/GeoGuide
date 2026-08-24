"""Identify what event sits at each location on the arena.

Grabs a high-resolution frame of the arena, isolates the five printed event
images by contour, classifies each one with a fine-tuned InceptionV3 model, and
writes the result to a pickle that ``control_center.py`` reads to plan its route.

Run this once, before ``control_center.py``, with the arena laid out and the
overhead camera in position. Press ``q`` in the live feed window to take the
snapshot.
"""

import pickle

import cv2 as cv
import numpy as np
from tensorflow import keras
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image

import config

event_snaps = []
event_regions = []
detected_events = []


def capture_arena(cap):
    """Show a live feed, then crop the arena out of the frame the user picks."""
    frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("error: failed to capture frame")
            break

        cv.namedWindow("live feed", cv.WINDOW_NORMAL)
        cv.resizeWindow("live feed", 500, 500)
        cv.imshow("live feed", frame)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()

    x, y, w, h = config.ARENA_CROP
    return frame[y:y + h, x:x + w]


def priority(item):
    """Sort key ordering events by how urgently the robot should visit them."""
    return config.EVENT_PRIORITY.index(item[1])


def locate_events(arena):
    """Find the printed event images on the arena and save a crop of each.

    The event images are bright rectangles against the arena, so a plain
    brightness threshold plus a contour pass isolates them. The size bounds
    exclude both noise and the much smaller ArUco markers.
    """
    gray = cv.cvtColor(arena, cv.COLOR_BGR2GRAY)
    _, thresholded = cv.threshold(gray, 195, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    area_threshold = 900

    for contour in contours:
        if cv.contourArea(contour) <= area_threshold:
            continue

        x, y, w, h = cv.boundingRect(contour)
        if not (90 <= w < 200 and 90 <= h < 200):
            continue

        event_image = arena[y:y + h, x:x + w]
        event_snaps.append(event_image)
        event_regions.append({"image": event_image, "coordinates": (x, y, w, h)})

    config.ARENA_DIR.mkdir(parents=True, exist_ok=True)
    for i, event_image in enumerate(event_snaps):
        # The JPEG quality flag has to be cast to int because of how the C
        # binding wraps the enum.
        cv.imwrite(
            str(config.ARENA_DIR / f"event_{i}.jpeg"),
            event_image,
            [int(cv.IMWRITE_JPEG_QUALITY), 100],
        )


def classify_event(model, image_path):
    """Return the (short label, full name) pair predicted for one event image."""
    img = image.load_img(image_path, target_size=(224, 224))
    x = np.expand_dims(img, axis=0)
    prediction = np.argmax(model.predict(preprocess_input(x)), axis=1)[0]
    return config.EVENT_NAMES[prediction]


def classify_all(arena):
    """Classify every located event and draw the labels back onto the arena."""
    model = keras.models.load_model(config.MODEL_PATH)

    for index, event_data in enumerate(event_regions):
        detected_event = classify_event(model, config.ARENA_DIR / f"event_{index}.jpeg")
        detected_events.append(detected_event)

        x, y, w, h = event_data["coordinates"]
        cv.rectangle(arena, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(
            arena, detected_event[0], (x, y - 10),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
        )

    cv.imshow("identified events", cv.resize(arena, (700, 700)))
    cv.waitKey(0)
    cv.destroyAllWindows()

    return detected_events


def main():
    cap = cv.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)

    arena = capture_arena(cap)
    locate_events(arena)
    classify_all(arena)

    # Events are found left-to-right, which matches location A through E.
    # Locations that came back blank hold no event and are dropped.
    identified_labels = {
        chr(i + 65): detected_events[i][1]
        for i in range(len(detected_events))
        if detected_events[i][1] != " "
    }

    # Stored in visit order so the control center can just walk the keys.
    identified_labels = dict(sorted(identified_labels.items(), key=priority))
    config.EVENTS_PICKLE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.EVENTS_PICKLE, "wb") as f:
        pickle.dump(identified_labels, f)

    print(dict(sorted(identified_labels.items())))


if __name__ == "__main__":
    main()
