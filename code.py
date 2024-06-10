import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import cv2
import numpy as np

# GPIO setup
GPIO.setmode(GPIO.BCM)
PIR_PIN = 17
LED_PIN = 18

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# Camera setup
camera = PiCamera()

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
                
                # Turn on LED
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                # Turn off LED
                GPIO.output(LED_PIN, GPIO.LOW)
            
            time.sleep(5)  # Debounce time
        else:
            # Ensure LED is off when no motion is detected
            GPIO.output(LED_PIN, GPIO.LOW)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
