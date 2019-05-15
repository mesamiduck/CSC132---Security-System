######################################
# Name: Austin Dardar
# Date: 5/?/2019
# Description: Security System GUI for CSC
######################################

###########
# Imports #
###########

from Tkinter import *
import RPi.GPIO as GPIO
from time import sleep, time
import pygame
import subprocess

###################
# Initializations #
###################

# initialize the pygame library
pygame.init()
# debug
DEBUG = False # debug mode, exits fullscreen
# the intruder sound if tripwire tripped
intruder = [pygame.mixer.Sound("Images/intruder.wav")]
# use the broadcom pin mode
GPIO.setmode(GPIO.BCM)
# constants
SETTLE_TIME = 2                  # seconds to let the sensor settle
CALIBRATIONS = 10                 # number of calibration measurements to take
CALIBRATION_DELAY = 1            # seconds to delay in between calibration measurements
TRIGGER_TIME = 0.0000001
SPEED_OF_SOUND = 343
calibrated = 0
tripwire_active = 0
speaker_active = 0
# setup GPIO pins
green = 6
yellow = 21
button = 25
red = 12
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # button near tripwire, user input can toggle off tripwire
GPIO.setup(green, GPIO.OUT) # Green LED (ultrasonic sensor)
GPIO.setup(yellow, GPIO.OUT) # yellow LED (speaker LED)
GPIO.setup(red, GPIO.OUT) # red LED to show tripwire has been tripped
GPIO.output(red, GPIO.LOW) # default red LED to off
GPIO.output(green, GPIO.LOW) # default green LED to off
GPIO.output(yellow, GPIO.LOW) # default yellow LED to off
TRIG = 18 # Ultrasonic sensor
ECHO = 27 # Ultrasonic sensor
GPIO.setup(TRIG, GPIO.OUT) # Ultrasonic sensor
GPIO.setup(ECHO, GPIO.IN) # Ultrasonic sensor

########
# Beef #
########

# The main GUI
class MainGUI(Frame):
    # the constructor
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="white")
        if (DEBUG):
            parent.attributes("-fullscreen", False)
        else:
            parent.attributes("-fullscreen", True)
        self.setupGUI()

    # Setup the GUI
    def setupGUI(self):
        self.display = Label(self, text="", anchor=CENTER, bg="grey", height=1, width=15, font=("TexGyreAdventor", 18))
        self.display.grid(row=2, column=0, columnspan=4, sticky=N+E+S+W)

        # the GUI layout
        # laser on off calibrate
        # speaker on off test
        # (LEDs will show the current setting)

        for row in range(3):
            Grid.rowconfigure(self, row, weight=1)
        for col in range(4):
            Grid.columnconfigure(self, col, weight=1)

        # The first row
        # tripwire
        img = PhotoImage(file="Images/tripwire.gif")
        button = Button(self, bg="red", image=img, borderwidth=5, highlightthickness=0, activebackground="red")
        button.image = img
        button.grid(row=0, column=0, sticky=N+S+E+W)
        # on
        img = PhotoImage(file="Images/on.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("laser_on"))
        button.image = img
        button.grid(row=0, column=1, sticky=N+S+E+W)
        # calibrate
        img = PhotoImage(file="Images/calibrate.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("laser_calibrate"))
        button.image = img
        button.grid(row=0, column=2, sticky=N+S+E+W)
        # quit
        img = PhotoImage(file="Images/quit.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("quit"))
        button.image = img
        button.grid(row=0, column=3, sticky=N+S+E+W)
        # speaker
        img = PhotoImage(file="Images/speaker.gif")
        button = Button(self, bg="red", image=img, borderwidth=5, highlightthickness=0, activebackground="red")
        button.image = img
        button.grid(row=1, column=0, sticky=N+S+E+W)
        # on (loud)
        img = PhotoImage(file="Images/on.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("speaker_on"))
        button.image = img
        button.grid(row=1, column=1, sticky=N+S+E+W)
        # off (stealth)
        img = PhotoImage(file="Images/off.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("speaker_off"))
        button.image = img
        button.grid(row=1, column=2, sticky=N+S+E+W)
        # test
        img = PhotoImage(file="Images/test.gif")
        button = Button(self, bg="black", image=img, borderwidth=5, highlightthickness=0, activebackground="white", command=lambda: self.process("speaker_test"))
        button.image = img
        button.grid(row=1, column=3, sticky=N+S+E+W)

        # pack the gui
        self.pack(fill=BOTH, expand=1)

    def process(self, button):
        global calibrated, tripwire_active, speaker_active
        if (button == "laser_on"):
            if (calibrated == 1): #Checks to see if the Ultrasonic was calibrated or not, if yes then continue
                GPIO.output(green, GPIO.HIGH)
                self.display["text"] = "Tripwire on standby. (Red LED: on=tripped, off=never tripped)"
                tripwire_active = 1
                tripwire_on()
            else:
                GPIO.output(green, GPIO.LOW) #Must be calibrated first
                self.display["text"] = "Tripwire must be calibrated first."
        elif (button == "quit"): # Just quits the program
            GPIO.cleanup()
            self.display["text"] = "Exiting program..."
            if (DEBUG):
                print("Terminated the program.")
            window.destroy()
        elif (button == "laser_calibrate"): # Initiates the laser calibration
            if (calibrated == 0): #If not calibrated already
                if (True): 
                    count = 0
                    while (count < 3): # Blink 3 times on GREEN LED to signify calibration
                        GPIO.output(green, GPIO.HIGH)
                        sleep(0.5)
                        GPIO.output(green, GPIO.LOW)
                        sleep(0.5)
                        count += 1
                tripwire_on() # Calibrate
                calibrated = 1 # Calibrated
                self.display["text"] = "Tripwire calibrated. (Green LED: on/off) (Button disables tripwire)"
            else:
                self.display["text"] = "Tripwire already calibrated."
        elif (button == "speaker_on"): # Use the speaker
            GPIO.output(yellow, GPIO.HIGH)
            self.display["text"] = "Speaker is on."
            speaker_active = 1
        elif (button == "speaker_off"): # Dont use the speaker
            GPIO.output(yellow, GPIO.LOW)
            self.display["text"] = "Speaker is off."
            speaker_active = 0
        elif (button == "speaker_test"): # Test the speaker, keep same setting of ON/OFF speaker
            self.display["text"] = "Speaker tested, should have sounded the alarm."
            intruder[0].play()
            count = 0
            while (count < 3): # Yellow LED blinks 3 time to show testing
                GPIO.output(yellow, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(yellow, GPIO.LOW)
                sleep(0.5)
                count += 1
            if (speaker_active == 1): # Keeps memory status of speaker setting prior to testing
                GPIO.output(yellow, GPIO.HIGH)
            else:
                GPIO.output(yellow, GPIO.LOW)

# Tripwire functions
# calculations
def tripwire_on():
    global calibrated, tripwire_active, distance_avg, tripped
    if (calibrated == 0): # if not calibrated, calibrate
        if (DEBUG):
            print "Calibrating..."
            # measure the distance to the object with the sensor
            # do this several times and get an average
            print "-Getting calibration measurements..."
        distance_avg = 0
        for i in range(CALIBRATIONS): # Essentially take the distance 10 times for an average and use that
            distance = getDistance()
            if (DEBUG):
                print "--Got {}cm".format(distance)
            # keep a running sum
            distance_avg += distance
            # delay a short time before using the sensor again
            sleep(CALIBRATION_DELAY)
        # calculate the average of the distances
        distance_avg /= CALIBRATIONS

        if (DEBUG):
            print "--Average is {}cm".format(distance_avg)
            print "Done."
            print
        return distance_avg
    elif(tripwire_active == 1): # Once calibrated, literally turn on the tripwire
        global speaker_active
        # next, reset the known_distance to the new one
        tripwire = distance_avg * 0.85 # takes 85% of the averaged distance to use as the tripwire range. Gives a little room for error as the sensor isnt perfect
        if (DEBUG):
            print "The tripwire range is: " + str(tripwire)
            print "Getting measurements:"
        count = 0
        while(tripwire_active == 1): # Have a count to counter random distances, the object has to be in the line of sight of the tripwire for 3 rounds of the distance check to trip
            GPIO.output(red, GPIO.LOW)
            if (GPIO.input(button) == GPIO.HIGH): # User pressed button to stop tripwire
                if (DEBUG):
                    print "User pushed button to manually stop laser."
                GPIO.output(green, GPIO.LOW)
                tripwire_active = 0
                break
            if (DEBUG):
                print "-Measuring..."
            distance = getDistance()
            sleep(0.05) # Each distance round time
            # and round to four decimal places
            distance = round(distance, 4)
            if (DEBUG):    
                # display the distance measured/calculated
                print "--Distance measured: {}cm".format(distance)
            if (distance < tripwire): # If distance is less, up the count
                count += 1 # Upping the count
                if (count > 2): # If the count is more than 2 times, trip the wire as it wasnt a random distance
                    if (DEBUG):
                        print "\nTripwire has been tripped!"
                    GPIO.output(red, GPIO.HIGH) # Turn RED led on to signify tripped wire
                    subprocess.call(['/home/pi/SecuritySystem/capture.sh']) # Initiate webcam to take picture
                    tripwire_active = 0 # Turn tripwire off
                    GPIO.output(green, GPIO.LOW) # Turn GREEN led off to signify the tripwire is no longer on
                    if (speaker_active == 1): # If the speaker setting is turned on, play the intruder noise
                        intruder[0].play()
            else: # Reset the count to cancel out the random distance calculations
                count = 0

# uses the sensor to calculate the distance to an object
def getDistance(): # getting the distances for the ultrasonic sensor
    # trigger the sensor by setting it high for a short time and
    # then setting it low
    GPIO.output(TRIG, GPIO.HIGH)
    sleep(TRIGGER_TIME)
    GPIO.output(TRIG, GPIO.LOW)
    # wait for the ECHO pin to read high
    # once the ECHO pin is high, the start time is set
    # once the ECHO pin is low again, the end time is set
    while (GPIO.input(ECHO) == GPIO.LOW):
        start = time()
    while (GPIO.input(ECHO) == GPIO.HIGH):
        end = time()
    # calculate the duration that the ECHO pin was high
    # this is how long the pulse took to get from the sensor to
    # the object -- and back again
    duration = end - start
    # calculate the total distance that the pulse traveled by
    # factoring in the speed of sound (m/s)
    distance = duration * SPEED_OF_SOUND
    # the distance from the sensor to the object is half of the
    # total distance traveled
    distance /= 2
    # convert from meters to centimeters
    distance *= 100
    return distance

if (DEBUG):
    print "Waiting for sensor to settle ({}s)...".format(SETTLE_TIME)
GPIO.output(TRIG,GPIO.LOW)
sleep(SETTLE_TIME)
if (DEBUG):
    print "Sensor settled: executing program."

########
# MAIN #
########

# Create the window
window = Tk()

# set window title
window.title("DBB Security System")

# generate the gui
p = MainGUI(window)

# display the gui and wait for user interaction
window.mainloop()
