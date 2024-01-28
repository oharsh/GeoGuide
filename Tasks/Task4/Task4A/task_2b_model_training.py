from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
from tensorflow.keras.models import Sequential
import cv2
import os
import numpy as np
from glob import glob


width, height = 224, 224 
train_images = []
train_path = "C:/Users/hp/train"

# List all image files in the train_path directory
train_files = [os.path.join(train_path, file) for file in os.listdir(train_path) if file.endswith('.jpeg')]

for path in train_files:
    img = cv2.imread(path)
    if img is not None:
        img = cv2.GaussianBlur(img, (5, 5), 0)
        train_images.append(cv2.resize(img, (width, height)))
    else:
        print(f"Warning: Image not found or could not be read at path: {path}")

test_images = []
test_path = 'C:/Users/hp/test'

# List all image files in the test_path directory
test_files = [os.path.join(test_path, file) for file in os.listdir(test_path) if file.endswith('.jpeg')]

for path in test_files:
    img = cv2.imread(path)
    if img is not None:
        img = cv2.GaussianBlur(img, (5, 5), 0)
        test_images.append(cv2.resize(img, (width, height)))
    else:
        print(f"Warning: Image not found or could not be read at path: {path}")


IMAGE_SIZE = [224, 224]
from tensorflow.keras.applications.inception_v3 import InceptionV3
inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)


for layer in inception.layers:
    layer.trainable = False
    
folders = glob('C:/Users/hp/train/*')


from keras.layers import Dense, Activation, Flatten
x = Flatten()(inception.output)

prediction = Dense(len(folders), activation='softmax', input_dim=10)(x)

# create a model object
from tensorflow import keras
model = keras.Model(inputs=inception.input, outputs=prediction)

model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)


train_datagen = ImageDataGenerator(rescale = 1./255,
                                   shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True)

test_datagen = ImageDataGenerator(rescale = 1./255)

training_set = train_datagen.flow_from_directory('C:/Users/hp/train',
                                                 target_size = (224, 224),
                                                 batch_size = 64,
                                                 class_mode = 'categorical',
                                                 classes=['Combat', 'Humanitarian Aid and rehabilitation', 'Military vehicles and weapons', 'Fire', 'DestroyedBuildings'])

test_set = test_datagen.flow_from_directory('C:/Users/hp/test',
                                            target_size = (224, 224),
                                            batch_size = 64,
                                            class_mode = 'categorical',
                                            classes= ['Combat', 'Humanitarian Aid and rehabilitation', 'Military vehicles and weapons', 'Fire', 'DestroyedBuildings'])


try:
    r = model.fit(
      training_set,
      validation_data=test_set,
      epochs=15,
      steps_per_epoch=len(training_set),
      validation_steps=len(test_set)
    )
except Exception as e:
    print("An error occurred:", str(e))
    

model.save('object_classification.h5')