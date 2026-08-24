"""Fine-tune InceptionV3 to classify the five arena event images.

Loads ImageNet-pretrained InceptionV3, freezes the convolutional base, and
trains a fresh softmax head on the event dataset. The result is saved to
``models/object_classification.h5``, which ``control_center/event_detection.py``
loads at run time.

Expects the dataset unpacked into one directory per class:

    runtime/dataset/train/<class>/*.jpeg
    runtime/dataset/test/<class>/*.jpeg

The zipped source images are in ``data/datasets/``.
"""

import os

from tensorflow import keras
from tensorflow.compat.v1 import ConfigProto, InteractiveSession
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Cap GPU memory so the session shares the card rather than grabbing all of it.
config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_DIR = os.environ.get("GEOGUIDE_TRAIN_DIR", os.path.join(ROOT_DIR, "runtime", "dataset", "train"))
TEST_DIR = os.environ.get("GEOGUIDE_TEST_DIR", os.path.join(ROOT_DIR, "runtime", "dataset", "test"))
MODEL_OUT = os.path.join(ROOT_DIR, "models", "object_classification.h5")

IMAGE_SIZE = [224, 224]
BATCH_SIZE = 64
EPOCHS = 15

# Class order here fixes the model's output indices. It must stay in step with
# EVENT_NAMES in control_center/config.py.
CLASSES = [
    "Combat",
    "Humanitarian Aid and rehabilitation",
    "Military vehicles and weapons",
    "Fire",
    "DestroyedBuildings",
]

# Frozen ImageNet base -- only the classifier head below is trained.
inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights="imagenet", include_top=False)
for layer in inception.layers:
    layer.trainable = False

x = Flatten()(inception.output)
prediction = Dense(len(CLASSES), activation="softmax")(x)

model = keras.Model(inputs=inception.input, outputs=prediction)
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

# The arena images are photographed under varying light and angle, so the
# training set is augmented while the test set is only rescaled.
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
)
test_datagen = ImageDataGenerator(rescale=1.0 / 255)

training_set = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    classes=CLASSES,
)
test_set = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    classes=CLASSES,
)

model.fit(
    training_set,
    validation_data=test_set,
    epochs=EPOCHS,
    steps_per_epoch=len(training_set),
    validation_steps=len(test_set),
)

os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
model.save(MODEL_OUT)
print(f"saved model to {MODEL_OUT}")
