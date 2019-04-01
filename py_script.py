# import the necessary packages
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
from imutils import face_utils
import imutils 
import dlib
import cv2
import array as arr
import numpy as np
from scipy.spatial import distance as dist
import cups
import textwrap 
import os
#physiognomy code
eye_range = arr.array('f', [0.2, 0.25, 0.3])
brow_range= arr.array('f', [0.75, 0.85, 0.95])
nose_range = arr.array('f', [0.25, 0.37, 0.45])
nostril_range = arr.array('f', [0.15, 0.2, 0.25])
mouth_range = arr.array('f', [0.30, 0.35, 0.40])
lip_range = arr.array('f', [0.18, 0.23, 0.28])

def physiognomize_eyes(dist, height):
    description = ""
    if dist >= eye_range[2]:
        description += "When the eyes are unusually far apart, the subject will have great powers of observation and a good memory for places, faces, etc., but he will be deficient in logic and reason."
    if dist <= eye_range[0]:
        description += "Eyes which approach the nose closely give a singularly disagreeable expression to the face. This peculiarity indicates a nature inclined to be narrow in its outlook on life."
    if height <= 0.06:
        description += "A cast or squint in the eye can be a sign of moral depravity."
    return textwrap.fill(description, 32)

def physiognomize_mouth(width, height):
    description = "The mouth is the great indicator of the animal passions. It shows how far the individual is governed by the senses, and the degree of his self-control."
    if width <= mouth_range[0]:
        description += "A short mouth shows coldness, littleness, pettiness, weakness."
    if width > mouth_range[1] and width < mouth_range[2]:
        description += "A wide mouth indicates geniality, toleration, sympathy."
    if width >= mouth_range[2]:
        description += "A very wide mouth indicates lack of restraint."
    if height <= lip_range[0]:
        description += "Thin lips: extreme fineness and narrowness of lips denote moderation, extreme coldness, spite, industry, order, endurance and self-denial."
    if height > lip_range[0] and height < lip_range[1]:
        description += "Medium lips:Fairly full lips show  generosity, ardor, affection, enthusiasm, quick temper and activity."

    if height >= lip_range[1] and height < lip_range[2]:
        description += "Thick lips: thick lips denote love of the material, sensuality, amiability, laziness, geniality and laxity of principle."
    if height >= lip_range[2]: 
        description += "Voluminous lips: These are the lips of those who are entirely dominated by the senses."
    return textwrap.fill(description, 32)


def physiognomize_nose(width, length):
    print("nose width: ", width)
    print("nose length", length)
    print("nostril range at 1: ", nostril_range[1])
    print("nostril range: ", nostril_range)
    description = "Amongst the different races of the earth, the length of the nose is in exact ratio to the mental capacity. "
    if length < nose_range[1]:
        print("short nose")
        description += "Short nose: The nose is at its shortest in the negro race, the Esquimaux, the Aborigines of Australia, and the Papuans."
        if width >= nostril_range[1]:
            description += "short, wide nostrils: lack of will power, a great deal of aggressiveness, impudence, cheerfulness. When the tip is not too thick, wit and humor are indicated. A square thick tip denotes a certain dogged honesty. A dangerous little nose in a woman. The lack of force and determination so necessary to a man renders the woman but the more charming."
    if length >= nose_range[1]:
        print(" long nose")
        description += "Long nose: In the Mongolian, the nose is a little longer, and in the Caucasian it is at its longest."
    if width >= nostril_range[1]:
        description += "Broad nostriled nose: Clear perception, power of concentration, logic and reason. Quick decision in thought and action, and frequently rapid and fluent speech. This is the nose of the philosopher, the deep thinker, the mathematician, the originator. It expresses breadth in thought and action, geniality, a love of the practical rather than the ideal."
    if width > nostril_range[0] and width <= nostril_range[1]:
        description += "The Greek Nose: Nostrils are narrow and the lobes thin: self-contained, refined, sensitive nature. The temperament is artistic and poetic. There is a strong tendency to romance and sentiment, and a lack of practical talent. Coldness and egotism are often characteristics. Intense fastidiousness is also denoted."
    if width <= nostril_range[0]:
        description += "The pointed nose: thin in substance, straight line. Narrowness of outlook, egotism and refined cruelty, a cruelty which will torture by word or deed, exacting the utmost limit of suffering. Fanatics frequently possess such a feature."
    return textwrap.fill(description, 32)



#pin setup for push button
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
#printer
conn = cups.Connection()

printers = conn.getPrinters()

taking_picture = False

printer_name = list(printers.keys())[0]

#setup text for printing

#
p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

camera = PiCamera()
camera.resolution = (1024, 768)


def take_picture():

  textfile = open('textfile.txt', 'w')
  textfile.seek(0)
  textfile.truncate()
  print("hitting function")
  camera.start_preview()
  # # Camera warm-up time
  sleep(2)
  camera.capture('file.jpg')
  
  # initialize dlib's face detector (HOG-based) and then create
   # the facial landmark predictor
  
    # load the input image and convert it to grayscale
  image = cv2.imread("file.jpg")
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  
  # detect faces in the grayscale image
  rects = detector(gray, 1)
  
  # loop over the face detections
  for (i, rect) in enumerate(rects):
      # determine the facial landmarks for the face region, then
      # convert the facial landmark (x, y)-coordinates to a NumPy
                  # array
      shape = predictor(gray, rect)
      shape = face_utils.shape_to_np(shape)
    # get euclidean dist for different parts of face using comparison to face width and length
    # TODO: add angle of nose, nose bridge, etc.
      face_width = dist.euclidean(shape[0], shape[16])
      face_length = (dist.euclidean(shape[0], shape[8]) + dist.euclidean(shape[16], shape[8]))/2
      # ratio of eye distance to face width
      eye_dist = round(dist.euclidean(shape[39], shape[42])/face_width, 2)
      textfile.write("Eye distance :"+ str(eye_dist) + "\n")
      eye_height = round(dist.euclidean(shape[37], shape[41])/face_length, 2)
      textfile.write("Eye height: " + str(eye_height) + "\n")
      eye_desc = physiognomize_eyes(eye_dist, eye_height)
      textfile.write(eye_desc + "\n")
      brow_dist = round(dist.euclidean(shape[17], shape[26])/face_width, 2)
      #not using this for now textfile.write("Brow distance: "+ str(brow_dist) + "\n")
      nostril_width = round(dist.euclidean(shape[31], shape[35])/face_width, 2)
      textfile.write( "Nostril width: " + str(nostril_width) + "\n")
      nose_length = round(dist.euclidean(shape[27], shape[33])/face_length, 2)
      nose_desc = physiognomize_nose(nostril_width, nose_length)
      textfile.write("Nose length: "+ str(nose_length) + "\n")
      textfile.write(nose_desc + "\n")
      mouth_width = round(dist.euclidean(shape[48], shape[54])/face_width, 2)
      textfile.write("Mouth width: "+ str(mouth_width) + "\n")
      lip_height = round(((dist.euclidean(shape[50], shape[57]) + dist.euclidean(shape[52], shape[58])/2)/face_length), 2)
      mouth_desc = physiognomize_mouth(mouth_width, lip_height)
      textfile.write("Lip height: "+ str(lip_height) + "\n\n\n\n")
      textfile.write(mouth_desc + "\n")


    # loop over the face parts individually
      for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
        # display the name of the face part on the image
            cv2.putText(image, name, (shape[i: j][0, 0], shape[i: j][0, 1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                             
        # loop over the subset of facial landmarks, drawing the
                # specific face part
#            oldx = False
#            oldy = False
# old code to draw lines and circles on features for testing
#            for (x, y) in shape[i:j]:
#                if oldx != False and oldy != False:
#                   cv2.line(image, (x, y), (oldx, oldy), (0, 0, 255), 1, 8, 0)
#                oldx = x
#                oldy = y
                # loop over the (x, y)-coordinates for the facial landmarks
                    # and draw them on the image
#                cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
            # extract the ROI of the face region as a separate image
 #               (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
 #               roi = image[y:y + h, x:x + w]
                #roi = imutils.resize(roi, width=250, inter=cv2.INTER_CUBIC)
                                         
    # visualize all facial landmarks with a transparent overlay
      output = face_utils.visualize_facial_landmarks(image, shape)
    
# show the output image with the face detections + facial landmarks
      cv2.imwrite("output.jpg", output)
      print("function complete")
      cv2.destroyAllWindows()
  #print image and text
  textfile.close()
  print_id = conn.printFile(printer_name, './output.jpg', "test_output", {})
  print_id2 = conn.printFile(printer_name, os.path.abspath('textfile.txt'), "text_output", {"cpi": "17", "lpi":"7", "l": "true"})
  #empty text file
  sleep(3)
  taking_picture = False
  #TODO:  Wait until the job finishes

while True:
    if GPIO.input(11) == GPIO.HIGH and taking_picture == False: 
        take_picture()
        taking_picture == True
        


        

eye_dict = {
        "low": "",
        "medium": "",
        "high": ""
        }
brow_dict = {
        "low": "",
        "medium": "",
        "high": ""
        }
nose_dict = {
        "low": "",
        "medium": "",
        "high": ""
        }
nostril_dict = {
        "low": "",
        "medium": "",
        "high": ""
        }
mouth_dict = {
        "low": "",
        "medium": "",
        "high": ""
        }

