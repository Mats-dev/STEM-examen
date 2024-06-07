import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import cv2

# Initialisatie
camera = PiCamera()
PIR_PIN = 17
LED_PIN = 27

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# Functie om foto te maken
def take_photo():
    timestamp = int(time.time())
    photo_path = f"/home/pi/photos/photo_{timestamp}.jpg"
    camera.capture(photo_path)
    return photo_path

# Functie om foto te verwerken en afval te identificeren
def process_photo(photo_path):
    img = cv2.imread(photo_path)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Definieer kleurgrenzen voor verschillende afvalcategorieën
    # Groen voor organisch
    green_lower = (40, 40, 40)
    green_upper = (70, 255, 255)

    # Blauw voor papier
    blue_lower = (100, 150, 0)
    blue_upper = (140, 255, 255)

    green_mask = cv2.inRange(hsv_img, green_lower, green_upper)
    blue_mask = cv2.inRange(hsv_img, blue_lower, blue_upper)

    green_count = cv2.countNonZero(green_mask)
    blue_count = cv2.countNonZero(blue_mask)

    if green_count > blue_count:
        return "Organisch afval", 10
    elif blue_count > green_count:
        return "Papier", 5
    else:
        return "Overig afval", 1

try:
    print("Sensor initializing...")
    time.sleep(2)  # Tijd om de sensor te laten stabiliseren
    print("Sensor ready")

    while True:
        if GPIO.input(PIR_PIN):
            print("Beweging gedetecteerd!")
            GPIO.output(LED_PIN, GPIO.HIGH)

            photo_path = take_photo()
            afvalsoort, punten = process_photo(photo_path)
            print(f"Gedetecteerd: {afvalsoort}, Punten: {punten}")

            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(5)  # Pauze om meerdere detecties snel na elkaar te voorkomen
        time.sleep(1)

except KeyboardInterrupt:
    print("Script gestopt door gebruiker")

finally:
    GPIO.cleanup()
