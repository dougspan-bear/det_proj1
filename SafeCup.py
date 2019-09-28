import os
import io
import re
import time
#import config
import picamera
from time import sleep
from google.cloud import vision
from PIL import Image, ImageDraw
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel
from google.protobuf.json_format import MessageToDict

#setting up pushdown buttons
ss = crickit.seesaw
BUTTON_LOCK_UNLOCK = crickit.SIGNAL1
BUTTON_HELP = crickit.SIGNAL2
ss.pin_mode(BUTTON_LOCK_UNLOCK, ss.INPUT_PULLUP)
ss.pin_mode(BUTTON_HELP, ss.INPUT_PULLUP)

#Set global variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/DET_JsonKey.json"
client = vision.ImageAnnotatorClient()
image = 'image.jpg'

#initialize LEDs and color states
num_pixels = 9
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)


def lights(state):
    # controls light behavior. Does not handle interrupts
    # lights begin and end with each LED in the off state

    pixels.fill(OFF)
    pixels.show()

    if state == 'ID_scanning':
        #blue lights move across the LED strip
        for i in range(num_pixels):
            pixels.fill(OFF)
            pixels[i] = BLUE
            pixels.show()
            time.sleep(.2)

    elif state == 'ID_registered':
        #green light turns on for 1 second
        pixels.fill(GREEN)
        pixels.show()
        time.sleep(1)

    elif state == 'cup_locked':
        #green light flashes quickly twice
        for i in range(2):
            pixels.fill(BLUE)
            pixels.show()
            time.sleep(.25)
            pixels.fill(OFF)
            pixels.show()
            time.sleep(.25)

    elif state == 'ID_wrong':
        #red light flashes quickly twice
        for i in range(4):
            pixels.fill(RED)
            pixels.show()
            time.sleep(.25)
            pixels.fill(OFF)
            pixels.show()
            time.sleep(.25)

    elif state == 'ID_correct':
        #green light flashes slowly once
        pixels.fill(GREEN)
        pixels.show()
        time.sleep(1.0)
    else:
        print("lights state undefined")

    pixels.fill(OFF)
    pixels.show()
    return True

def servo(state):
    #controls servo angle to lock/unlock the safecup
    if state =='lock':
        crickit.servo_1.angle = 180
    elif state =='unlock':
        crickit.servo_1.angle = 75
    return True

def readImg(path):
    # returns the drivers license number if DL is detected
    # returns cropped image of the largest face in the image if face detected and no DL number found
    # returns empty array if no face or no drivers license found

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    faceOrID, content = readID(image)
    if not faceOrID:
        faceOrID, content = readFace(image)
    return faceOrID, content


def readID(image):
    # Only handles california driver's licenses
    # Return empty string if no ID found
    # Return drivers license number as a string if ID found
    id = None
    idStr = ''

    response = client.text_detection(image=image)
    texts = response.full_text_annotation.text
    #matches = re.search("\\nDL\s(.+)\\nEXP", texts)
    matches = re.search("[a-zA-Z]{1}[0-9]{7}", texts)
    if matches:
        id = matches[0]
        idStr = 'ID'

    return idStr, id


def readFace(image):
    faceConfidence = 0.8
    faceStr = ''
    face = None
    
    response = client.face_detection(image=image)
    if response.face_annotations:
        faces = MessageToDict(response)['faceAnnotations']
        for face in faces:
            if face['detectionConfidence'] > faceConfidence:
                if face['angerLikelihood'] == "LIKELY" or face['angerLikelihood'] == "VERY_LIKELY" or\
                    face['sorrowLikelihood'] == "LIKELY" or face['sorrowLikelihood'] == "VERY_LIKELY"or\
                    face['angerLikelihood'] == "POSSIBLE" or face['sorrowLikelihood'] == "POSSIBLE":
                    faceStr = 'FACE'
    return faceStr, face


def textFace(imagePath, content, id):
    bounds = content['fdBoundingPoly']['vertices']
    image = Image.open(imagePath)
    # x_min, y_min, x_max, y_max
    xs, ys = [], []
    for vertex in bounds:
        for k, v in vertex.items():
            if k == 'x':
                xs.append(v)
            elif k == 'y':
                ys.append(v)
    imCropped = image.crop((min(xs), min(ys), max(xs), max(ys)))
    imCropped.save('croppedImg.jpg')
        
    print('texting face to phone. ')

# Import smtplib for the actual sending function
import smtplib

# And imghdr to find the types of our images
import imghdr

# Here are the email package modules we'll need
from email.message import EmailMessage

def sendEmail():
    # Create the container email message.
    msg = EmailMessage()
    msg['Subject'] = 'Customer is in Danger'
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = 'ste.daff@gmail.com'
    msg['To'] = 'stephaniecd@berkley.edu'
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Open the files in binary mode.  Use imghdr to figure out the
    # MIME subtype for each specific image.
    with open('croppedImg.jpg', 'rb') as fp:
        img_data = fp.read()
    msg.add_attachment(img_data, maintype='image',
                                 subtype=imghdr.what(None, img_data))

    # Send the email via our own SMTP server.
    with smtplib.SMTP('smtp.gmail.com') as s:
        s.connect('smtp.gmail.com', 587)
        s.login('ste.daff', config.GMAIL_PW)
        s.send_message(msg)
        s.quit()

def takephoto(camera):
    # this triggers an on-screen preview, so you know what you're photographing!
    #camera.start_preview(alpha=180)
    sleep(.5)                   #give it a pause so you can adjust if needed
    camera.capture('image.jpg') #save the image
    sleep(.5)
    #camera.stop_preview()       #stop the preview


def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts


def main():
    #runs a forever while loop when the function starts.
    # System state initializes with no ID registered
    # System states and transitions are:

    # scanning ID       initial state. DL is an empty string.
    #                   Can only return to this state by
    #                   restarting program
    #
    # ID_registered     DL is a non-empty string
    # locked            DL is a non-empty string and button is pressed
    #

    #initialize program loop
    ID = ''
    pathToImg = 'image.jpg'
    camera = picamera.PiCamera()
    servo('lock')

    while True:
        
        if not ID:
            print('ID not loaded yet')
            lights('ID_scanning')
            
            takephoto(camera)
            faceOrID, content = readImg(pathToImg)
            print("Found %s : %s" % (faceOrID, content))

            if faceOrID == 'ID':
                ID = content
                print('ID loaded', ID)
                lights('ID_registered')
                servo('unlock')

                
        elif ID and not ss.digital_read(BUTTON_LOCK_UNLOCK):
                 
            print('lock button pressed')
            servo('lock')
            lights('cup_locked')
            
            pushCounter += 0.5

            if pushCounter >= 2:
                print("get Help")
                lights('ID_wrong')
                pushCounter = 0
            time.sleep(0.5)
        
        elif ID:
            takephoto(camera)
            faceOrID, content = readImg(pathToImg)
            print("Found %s : %s" % (faceOrID, content))          
        
            if not faceOrID:
                print('no face or ID found')
            if faceOrID == 'FACE':
                print('stranger danger')
                lights('ID_wrong')
                textFace(pathToImg, content, ID)
            if faceOrID == 'ID':
                if content == ID:
                    print('ID correct')
                    lights('ID_correct')
                    servo('unlock')
                else:
                    print('ID wrong')
                    lights('ID_wrong')

        else:
            print('something went wrong in ID loop')
        
        pushCounter = 0

if __name__== '__main__':
    print("Started")
    
    main()
