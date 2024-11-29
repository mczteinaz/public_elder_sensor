# LCD driver and code taken from manufacturer git repository at https://github.com/UCTRONICS/KB0005
# PIR motion detection code retrieved from ChatGPT queries and modified to fit specific purpose.
# DHT22 code taken from thezanshow's tutorial (https://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-26)
# DHT22 code uses pigpio from https://abyz.me.uk/rpi/pigpio/
# Pushbullet API information taken from https://docs.pushbullet.com/
# This code is Version 1111.3 / filename elder_code_version1111.3.py / 11-11-2024
# This code was compiled by mcardinal@cnm.edu for the elder_sensor IoT project
# Central Community College of New Mexico - IoT (U01) with Kerry Bruce - Fall 2024

# Import libraries
import RPi.GPIO as GPIO
import time
import I2C_LCD_driver
from datetime import datetime
import threading
import pigpio
import DHT22
from pushbullet import Pushbullet
import signal


# Initialize DHT22 sensor and run 1st trigger to discard bad value
pi = pigpio.pi()
dht22 = DHT22.sensor(pi, 17)  
dht22.trigger()
first_humidity, first_temp = dht22.humidity(), dht22.temperature()

# Set up LCD screen as mylcd
mylcd = I2C_LCD_driver.lcd()

# Set up GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set up GPIO pins
pir_sensor = 4  
green_led = 19  

# Set up the PIR sensor as an input
GPIO.setup(pir_sensor, GPIO.IN)

# Set up the green LED as an output
GPIO.setup(green_led, GPIO.OUT)

# Turn on the green LED to show the code started
GPIO.output(green_led, GPIO.HIGH)

# Pushbullet API configuration
api_key = "MY_KEY_HERE"
pb = Pushbullet(api_key)

# Pushbullet channel location to allow pushing to a channel
channel = next((ch for ch in pb.channels if ch.channel_tag == 'cnm_iot_project'), None)

# Set f_date_time variable to N/A before so it is valid throughout code
f_date_time = "N/A"  


# Create the flag to control threads
stop_event = threading.Event()  

# Setup function to trigger temp / humidity and present in desired format
def readDHT22():
    dht22.trigger()
    humidity = '%.2f' % (dht22.humidity())
    temp = '%.2f' % (dht22.temperature())
    temp_f = float(temp) * (9 / 5) + 32
    return humidity, "{:.1f}".format(temp_f)

try:
    while True:
        # Display date and time on LCD
        mylcd.lcd_display_string("%s" % time.strftime("    %I:%M %p"), 1)
        mylcd.lcd_display_string("%s" % time.strftime("  %b %d, %Y"), 2)
        # Set motion_detected initial flag state 
        motion_detected = False
        start_time = time.time()

        # Monitor for motion for 60 seconds
        while time.time() - start_time < 60:
            if GPIO.input(pir_sensor):
                motion_detected = True
                date_time = datetime.now()
                f_date_time = date_time.strftime("%m-%d-%Y %I:%M %p")
            # Wait a tenth of a second between motion detection checks so CPU is not flooded
            time.sleep(0.1)
        # Read temperature and humidity
        humidity, temperature_f = readDHT22()


        # Set pushbullet notification content based on motion detection
        if motion_detected:
            body = f"Motion detected during the monitoring period at {f_date_time}. Temp: {temperature_f}F Humidity: {humidity}%"
        # Send motion detected push notification as both push and to channel
            push = pb.push_note("Elder Sensor Report", body)
            push = channel.push_note("Elder Sensor Report", body)

        else:
            body = f"No motion detected during the monitoring period. Last motion detected at {f_date_time}. Temp: {temperature_f}F Humidity: {humidity}%"
            # Send no motion detected push notification as both push and to channel
            push = pb.push_note("Elder Sensor Report", body)
            push = channel.push_note("Elder Sensor Report", body)

finally:
    # Trigger the stop event to clean up the thread
    stop_event.set()
    GPIO.output(green_led, GPIO.LOW)
    mylcd.lcd_clear()
    mylcd.lcd_display_string("    WARNING!", 1)
    mylcd.lcd_display_string("App has stopped", 2)
    GPIO.cleanup()

