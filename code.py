import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import cv2
import numpy as np

# GPIO setup
GPIO.setmode(GPIO.BCM)
PIR_PIN = 17
SERVO_PIN = 18

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Camera setup
camera = PiCamera()

# Function to open and close the lid
def open_lid():
    pwm.ChangeDutyCycle(7)  # adjust as necessary
    time.sleep(1)

def close_lid():
    pwm.ChangeDutyCycle(2)  # adjust as necessary
    time.sleep(1)

def recognize_trash(image):
    # Load your pre-trained model
    net = cv2.dnn.readNet('model_path', 'config_path')
    blob = cv2.dnn.blobFromImage(image, 1.0, (224, 224), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    # Process detections and identify trash
    # For simplicity, let's assume detections return a label and confidence
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # confidence threshold
            label = int(detections[0, 0, i, 1])
            return label
    return None

try:
    while True:
        if GPIO.input(PIR_PIN):
            open_lid()
            time.sleep(2)
            
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
            
            close_lid()
            time.sleep(5)  # Debounce time

except KeyboardInterrupt:
    pass

finally:
    pwm.stop()
    GPIO.cleanup()
