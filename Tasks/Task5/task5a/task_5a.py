'''
*****************************************************************************************
*
*        		===============================================
*           		Geo Guide (GG) Theme (eYRC 2023-24)
*        		===============================================
*
*  This script is to implement Task 4A of Geo Guide (GG) Theme (eYRC 2023-24).
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''

# Team ID:			[ Team-ID ]
# Author List:		[ Names of team members worked on this file separated by Comma: Name1, Name2, ... ]
# Filename:			task_4a.py


####################### IMPORT MODULES #######################
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
##############################################################



################# ADD UTILITY FUNCTIONS HERE #################

"""
You are allowed to add any number of functions to this code.
"""

# arena_path = "captured_frame.jpg"
arena_path = "C:/Users/hp/2image_Arena/2024-02-04-012340.jpg"
event_list = []
detected_list = []
coordinate_list = []

combat = "combat"
rehab = "humanitarianaid"
military_vehicles = "militaryvehicles"
fire = "fire"
destroyed_building = "destroyedbuilding"
numbers = 'numbers'

#cap = cv.VideoCapture(0)

def arena_image(arena_path):   
    # while True:
    #     # Capture frame-by-frame
    #     ret, frame = cap.read()
    
    #     # Check if the frame was captured successfully
    #     if not ret:
    #         print("Error: Failed to capture frame")
    #         break
    
    #     # Display the frame
    #     cv.namedWindow("Live Feed", cv.WINDOW_NORMAL)
    #     cv.resizeWindow("Live Feed", 490, 490)
    #     cv.imshow('Live Feed', frame)
    
    #     # Save the frame to an image file (change the file name as needed)
    #     cv.imwrite('captured_frame.jpg', frame)

    #     if cv.waitKey(1) & 0xFF == ord('q'):
    #         break
    
    # cap.release()
    # cv.destroyAllWindows()
    frame = cv.imread(arena_path)
    
    y=0
    x=400
    h=1100
    w=1100
    cropped = frame[y:y+h, x:x+w]
    arena = cv.resize(cropped, (700, 700))
    return arena 

def event_identification(arena): 
    gray = cv.cvtColor(arena, cv.COLOR_BGR2GRAY)
   
    _, thresholded = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_threshold = 800

    event_list = []

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
        cv.imwrite(f'event_{i}.jpeg', event_image, [int(cv.IMWRITE_JPEG_QUALITY), 95])



def classify_event(image_path):
    
    model = keras.models.load_model("C:/Users/hp/object_classification_Final.h5")
    
    img=image.load_img(image_path,target_size=(224,224))
    x=image.img_to_array(img)
    x=np.expand_dims(img,axis=0)
    img_data=preprocess_input(x)
    a=np.argmax(model.predict(img_data), axis=1)[0]
    
    event_names = ['combat', 'human_aid_rehabilitation', 'military_vehicles', 'fire', 'destroyed_buildings', 'numbers'] 
    event = event_names[a]

    return event


def classification(coordinate_list,arena):
    
    
    for img_index, event_data in enumerate(coordinate_list):
        img = "C:/Users/hp/event_"+str(img_index)+".jpeg"
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
    arena = arena_image(arena_path)
    event_identification(arena)
    classification(coordinate_list, arena)
    
    if (detected_list[0] != 'numbers'):
        new_label = "A"
        new_value = str(detected_list[0])  
        identified_labels[new_label] = new_value
        
    if (detected_list[1] != 'numbers'):
        new_label = "B"
        new_value = str(detected_list[1])
        identified_labels[new_label] = new_value
        
    if (detected_list[2] != 'numbers'):
        new_label = "C"
        new_value = str(detected_list[2])
        identified_labels[new_label] = new_value
        
    if (detected_list[3] != 'numbers'):
        new_label = "D"
        new_value = str(detected_list[3])
        identified_labels[new_label] = new_value
        
    if (detected_list[4] != 'numbers'):
        new_label = "E"
        new_value = str(detected_list[4])
        identified_labels[new_label] = new_value

    # identified_labels = {"A": str(detected_list[0]), "B": str(detected_list[1]), 
    #                      "C": str(detected_list[2]), "D": str(detected_list[3]), 
    #                      "E": str(detected_list[4])}

    return identified_labels

if __name__ == "__main__":
    identified_labels = task_4a_return()
    print(identified_labels)
