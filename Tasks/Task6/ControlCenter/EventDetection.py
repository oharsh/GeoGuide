'''
* Team Id :         1667
* Author List :     Arijit Goswami, Gaurav Singh, Harsh Yadav, Abhishek Ranjan
* 
* Filename:         task5a_1.py
* Theme:            GeoGuide
* Functions:        arena_image(str), event_locator(arena), classify_event(str), classification(event_complete_info,arena), 
*                   task_4a_return(), priority()
*
* Global Variables: arena_path, model_path, cap, event_snap, event_complete_info, detected_list,

'''


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

#defining path to the arena and model file
arena_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/arena/"
model_path = "/home/deadmonk/Desktop/eyrc23_GG_1667/Resources/object_classification.h5"

#capture object
cap = cv.VideoCapture(2)

#setting property of cap object
desired_height = 1080
desired_width = 1920

cap.set(cv.CAP_PROP_FRAME_WIDTH, desired_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, desired_height)



event_snap = []
event_comp_info = []
detected_list = []


'''
* Function Name:   arena_image
* Input:           None.
* Output:          Cropped Arena Image 
* Logic:           This function will capture a frame of the arena and store the array in 
*                  a variable "frame"           
*
*
* Example Call:    arena_image()
'''
def arena_image():   
    while True:

        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame")
            break

        cv.namedWindow("Live Feed", cv.WINDOW_NORMAL)
        cv.resizeWindow("Live Feed", 500, 500)
        cv.imshow('Live Feed', frame)
    
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()

    #y, x: y and x are the coordinates used to crop the image   
    #w, h: w and h represent the height and width respectively of the modified arena 
    y=0
    x=400
    h=1050
    w=1050
    arena = frame[y:y+h, x:x+w]

    return arena 

    #toggle this to see the output image
    # return cv.imwrite(arena_path+"modified.jpg", arena)


'''
* Function Name:   priority
* Input:           a -> tuple containing dictionary objects
* Output:          return an integer based on the priority
* Logic:           this function is used to sort the dictionary on the basis of event priority.
*
* Example Call:    sorted(dict.items(), key=priority)
'''

def priority(a):
    if a[1] == "Fire":
        return 1
    if a[1] == "Destroyed buildings":
        return 2
    if a[1] == "Humanitarian Aid and rehabilitation":
        return 3
    if a[1] == "Military Vehicles":
        return 4
    if a[1] == "Combat":
        return 5
    if a[1] == " ":
        return 6


'''
* Function Name:   event_locator
* Input:           arena -> contains the cropped and resized arena image
* Output:          None
* Logic:           firstly this function will convert the color of the arena image from BGR to GRAY 
*                  and then it will give a particular threshold to the image and then it will set the 
*                  contours and area_threshold. It will detect images from the arena then it will append
*                  the detected images to the list named event_snap. Then it will append the detected images
*                  and its coordinates in the list named event_complete_info. Then the detected images
*                  will be saved in the particular path
*
*
* Example Call:    event_locator(arena)
'''

def event_locator(arena): 

    # Convert color from BGR to GRAY
    gray = cv.cvtColor(arena, cv.COLOR_BGR2GRAY)
    # Setting the Threshold Property 
    _, thresholded = cv.threshold(gray, 195, 255, cv.THRESH_BINARY)
    # Setting the Contours Property
    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # Setting the area threshold to remove unwanted detection
    area_threshold = 900


    # Iterate over the contours and retain only the event images
    for contour in contours:
        if cv.contourArea(contour) > area_threshold:
            x, y, w, h = cv.boundingRect(contour)

            # Exclude ARUCO markers (assuming ARUCO markers are small)
            if (w >= 90 and h >= 90) and (w<200 and h<200):

                #event_image: use to store individual event cordinates, width and height.
                event_image = arena[y:y+h, x:x+w]
                #event_snap: use to store event_image of every event location in a list.
                event_snap.append(event_image)
                #event_comp_info: It will store event image as well as their respective coordinates,
                #height, width.
                event_comp_info.append({"image": event_image, "coordinates": (x, y, w, h)})


    for i, event_image in enumerate(event_snap):

        #here we have to typecast cv.imwrite_jpeg_quality to int due to some c python wrapping issues
        cv.imwrite(f'{arena_path}event_{i}.jpeg', event_image, [int(cv.IMWRITE_JPEG_QUALITY), 100])

'''
* Function Name:   classify_event
* Input:           image_path -> path of the detected images from the arena.
* Output:          event      -> contains the predicted class of the image from the arena
* Logic:           firstly this function will load the trained model then it will resize the image and then
*                  convert the image to array. Then it will preprocess the expanded array then it will predict
*                  the class of the image
*
*
* Example Call:    classify_event(image_path)
'''

def classify_event(image_path):
    
  #Load the model
  model = keras.models.load_model(model_path)
  #Load image and resize it
  img=image.load_img(image_path,target_size=(224,224))
  #Converting image to its array counterpart
  x=image.img_to_array(img)
  #Expanding the dimesion of the array
  x=np.expand_dims(img,axis=0)

  img_data=preprocess_input(x)
  a=np.argmax(model.predict(img_data), axis=1)[0]
  
  event_names = [['combat', 'Combat'], ['humanitarian_aid', 'Humanitarian Aid and rehabilitation'], ['military_vehicles', 'Military Vehicles'], ['fire', 'Fire'], ['destroyed_buildings', 'Destroyed buildings'], [' ', ' ']] 
  #storing the event name based on the output 'a' from model.predict
  event = event_names[a]

  return event

'''
* Function Name:   classification
* Input:           event_complete_info -> contains the detected image from the arena and their coordinates
*                  arena           -> modified arena image
* Output:          return the list containing the predicted class of the detected images 
* Logic:           this function will iterate through all the images present in the event_complete_info
*                  and then it will fetch the image and classify the image and append the detected event
*                  in the detected_list after that the function will put the bounding boxes and predicted class
*                  on the identified image on the arena
*
*
* Example Call:    classification(event_complete_info,arena)
'''
def classification(event_comp_info,arena):
    
    
    for img_index, event_data in enumerate(event_comp_info):
        # Loading image path
        img = arena_path+"event_"+str(img_index)+".jpeg"
        # Predicting the image
        detected_event = classify_event(img)
        detected_list.append(detected_event)

        # Draw bounding box and add label to the image
        x, y, w, h = event_data["coordinates"]
        cv.rectangle(arena, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #Putting text on the images
        cv.putText(arena, detected_event[0], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    #New arena after drawing the bounding box
    new_arena = cv.resize(arena, (700, 700))
    cv.imshow('Identified Events', new_arena)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    return detected_list

'''
* Function Name:   main
* Input:           None
* Output:          it stores the identified labels dictionary as a events.pickle file which 
*                  can be accessed later.
*
* Logic:           All the magic happens here, it first calls arena_image() which creates 
*                  a arena object
*                  then using this arena image we find the locations of events on the arena
*                  event_locator returns event_comp_info which is then used by      
*                  classification function in order to classify events on the arena     
*                  the classes of events is then stored in detected_list[] in order of       
*                  their location      
*                  identified_label is a dictionary containing event location name 
*                  ie. A, B, C, D, E along with the events classes
*                  this dictionary is then sorted on the basis of priority using priority 
*                  function as a key in sorted function.
*                  the resultant dict is then stored as a pickle file which                  
*                  could be later used by the controlcenter to guide the robot.
*                  At last event_configuration is printed
* Example Call:    main()
'''

def main():

    identified_labels = {}  
    arena = arena_image()
    event_locator(arena)
    classification(event_comp_info, arena)

    identified_labels = {chr(i+65): detected_list[i][1] for i in range(0, len(detected_list)) if detected_list[i][1] != " "}

    identified_labels = dict(sorted(identified_labels.items(), key=priority))
    with open("/home/deadmonk/Desktop/eyrc23_GG_1667/Tasks/Task5/event/events.pickle", "wb") as f :
      pickle.dump(identified_labels, f)
    f.close()
    event_configuration = dict(sorted(identified_labels.items(), key= lambda a: a[0]))
    print(event_configuration)
    
if __name__ == "__main__":
  main()

