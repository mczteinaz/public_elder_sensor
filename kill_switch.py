# This code is Version 1 / filename kill_switch.py  / 11-11-2024
# GPIOZero library information for this code can be found at https://gpiozero.readthedocs.io/
# subprocess and os.system documnentation is available at https://docs.python.org/3/library/subprocess.html
# and was structured based on ChatGPT queries for how to stop a process and shutdown a system with python code
# This code was compiled by mcardinal@cnm.edu for the elder_sensor IoT project
# Central Community College of New Mexico - IoT (U01) with Kerry Bruce - Fall 2024

from gpiozero import Button
import os
import time
import subprocess

# Setup shutdown button on GPIO 16
shutdown_button = Button(16)  

# Define the shutdown function steps 
def shutdown():
    # Stop the elder_sensor.service
    subprocess.run(["sudo", "systemctl", "stop", "elder_sensor.service"])
    # Shutdown the system
    os.system("sudo shutdown -h now")
    # Restarting the code allows the shutdown to happen immediately
    subprocess.run(["sudo", "systemctl", "start", "elder_sensor.service"])
    

# When the button is pressed, trigger the shutdown function
shutdown_button.when_pressed = shutdown

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
