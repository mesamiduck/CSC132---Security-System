###################
# I tried to download fritzing and finding different LED colors, ultrasonic sensor, the 3v 5v breakout board, and I found no luck in anything so I just made a custom one into paint and hopefully that does the job


# You want the Capture.sh script in a folder called SecuritySystem
/home/pi/SecuritySystem/capture.sh

# You want the Images folder (contains .GIFs and the .WAV) in this directory
/home/pi/SecuritySystem/Images

# You want the SecurityGUI_001.py in the security systems folder
/home/pi/SecuritySystem/SecurityGUI_001.py

When the tripwire is tripped, your USB webcam (I have a logitech HD 720p) should take pictures at the
/home/pi/SecuritySystem/(PictureTaken.PNG) directory.

#################
Bill of Materials

USB webcam: $20/$30 at walmart or so

Raspberry Pi uses:
3 LEDs, 1 button, 1 ultrasonic sensor