import cv2 as cv
import os
from sys import platform
import numpy as np
import subprocess
import cv2 as cv  
import shutil
import ast
import sys
import os   
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
from tensorflow.keras.preprocessing import image
import pickle


arena_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/task5a/arena/"
model_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Resources/object_classification.h5"
# os.chdir(arena_path)
cap = cv.VideoCapture(2)


event_list = []
coordinate_list = []
detected_list = []

def arena_image(arena_path):   
    while True:

        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame")
            break

        cv.namedWindow("Live Feed", cv.WINDOW_NORMAL)
        cv.resizeWindow("Live Feed", 490, 490)
        cv.imshow('Live Feed', frame)
    
        cv.imwrite(arena_path+"arena.jpg", frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()
    # print(arena_path+arena_name)
    frame = cv.imread(arena_path+"arena.jpg")
    
    y=10
    x=90
    h=460
    w=470
    cropped = frame[y:y+h, x:x+w]
    arena = cv.resize(cropped, (700, 700))
    return arena 
    # return cv.imwrite(arena_path+"modified.jpg", arena)

def event_locator(arena): 
    gray = cv.cvtColor(arena, cv.COLOR_BGR2GRAY)
   
    _, thresholded = cv.threshold(gray, 190, 255, cv.THRESH_BINARY)

    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_threshold = 800


    # Iterate over the contours and retain only the event images
    for contour in contours:
        if cv.contourArea(contour) > area_threshold:
            x, y, w, h = cv.boundingRect(contour)

            # Exclude ARUCO markers (assuming ARUCO markers are small)
            if (w >= 40 and h >= 40) and (w<100 and h<100):
                event_image = arena[y:y+h, x:x+w]
                event_list.append(event_image)
                coordinate_list.append({"image": event_image, "coordinates": (x, y, w, h)})


    for i, event_image in enumerate(event_list):
        cv.imwrite(f'{arena_path}event_{i}.jpeg', event_image, [int(cv.IMWRITE_JPEG_QUALITY), 95])
 
def classify_event(image_path):
    
  model = keras.models.load_model(model_path)
  
  img=image.load_img(image_path,target_size=(224,224))
  x=image.img_to_array(img)
  x=np.expand_dims(img,axis=0)
  img_data=preprocess_input(x)
  a=np.argmax(model.predict(img_data), axis=1)[0]
  
  event_names = ['combat', 'human_aid_rehabilitation', 'military_vehicles', 'fire', 'destroyed_buildings', ' '] 
  event = event_names[a]

  return event


def classification(coordinate_list,arena):
    
    
    for img_index, event_data in enumerate(coordinate_list):
        img = arena_path+"event_"+str(img_index)+".jpeg"
        detected_event = classify_event(img)
        detected_list.append(detected_event)

        # Draw bounding box and add label to the image
        x, y, w, h = event_data["coordinates"]
        cv.rectangle(arena, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(arena, detected_event, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    new_arena = cv.resize(arena, (490, 465))
    cv.imshow('Identified Events', new_arena)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    return detected_list

def task_4a_return():

    identified_labels = {}  
    arena = arena_image(arena_path+"arena.jpg")
    event_locator(arena)
    classification(coordinate_list, arena)
    
    for i in range(len(detected_list)):
        if (detected_list[i] == 'fire'):
            new_label = chr(ord('A') + i)
            new_value = str(detected_list[i])
            identified_labels[new_label] = new_value
        
            
    for i in range(len(detected_list)):
        if(detected_list[i] == 'destroyed_buildings'):
            new_label = chr(ord('A') + i)
            new_value = str(detected_list[i])
            identified_labels[new_label] = new_value
            

    for i in range(len(detected_list)):
        if (detected_list[i] == 'human_aid_rehabilitation'):
            new_label = chr(ord('A') + i)
            new_value = str(detected_list[i])
            identified_labels[new_label] = new_value

            
        
    for i in range(len(detected_list)):
        if (detected_list[i] == 'military_vehicles'):
            new_label = chr(ord('A') + i)
            new_value = str(detected_list[i])
            identified_labels[new_label] = new_value
            
        
    for i in range(len(detected_list)):
        if (detected_list[i] == 'combat'):
            new_label = chr(ord('A') + i)
            new_value = str(detected_list[i])
            identified_labels[new_label] = new_value

    return identified_labels

def main():
  # arena_image(arena_path)
  # event_locator(arenaImage)
  identified_labels = task_4a_return()  
  with open("/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/task5a/event/events.pickle", "wb") as f :
    pickle.dump(identified_labels, f)
  f.close()

  dkey = identified_labels.keys()
  dkey = sorted(dkey)
  identified_labels = {i : identified_labels[i] for i in dkey}
  print(identified_labels)



if __name__ == "__main__":
  main()

