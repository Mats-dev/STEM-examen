import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import cv2
import numpy as np
from Adafruit_PN532 import PN532_I2C

# GPIO setup
GPIO.setmode(GPIO.BCM)
PIR_PIN = 17

GPIO.setup(PIR_PIN, GPIO.IN)

# Camera setup
camera = PiCamera()

# PN532 setup
pn532 = PN532_I2C(debug=False)
pn532.SAM_configuration()

# Function to recognize trash
def recognize_trash(image):
    # Load your pre-trained model
    net = cv2.dnn.readNet('model_path', 'config_path')
    blob = cv2.dnn.blobFromImage(image, 1.0, (224, 224), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    # Process detections and identify trash
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # confidence threshold
            label = int(detections[0, 0, i, 1])
            return label
    return None

# Function to read NFC tag
def read_nfc():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        return ''.join([format(i, '02X') for i in uid])
    return None

try:
    while True:
        if GPIO.input(PIR_PIN):
            # Capture image
            camera.capture('/home/pi/image.jpg')
            image = cv2.imread('/home/pi/image.jpg')
            
            # Recognize trash
            label = recognize_trash(image)
            
            if label is not None:
                print(f'Trash detected: {label}')
                # Assign points based on trash type
                points = 10  # Example, can be customized based on label
                print(f'Points awarded: {points}')
            
            # Read NFC tag
            nfc_id = read_nfc()
            if nfc_id is not None:
                print(f'NFC tag detected: {nfc_id}')
                # Here you can implement points assignment to a user account based on the NFC tag

            time.sleep(5)  # Debounce time

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
