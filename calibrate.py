# TODO
#

import board
import busio
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

import time

# importing pygame module
import pygame
import sys

# initialising pygame
pygame.init()

# creating display
display = pygame.display.set_mode((300, 300))

filename = "Samples.txt"

fnCount = 1

def saveCSV(filename, float_list):
    """Saves a CSV given the filename and list of values."""
    with open(filename, 'w') as file_object:
        for value in float_list:
            file_object.write(str(value) + "\n")
    print(f"{filename} has been saved.")


samples = []
currentSample = 0.0
startTime = time.time()
initialTimeLimit = 30.0

initFlag = True
counterFlag = False
continueFlag = False
counter = 0

print("Collecting initial samples. Please wait 30 seconds...")

while True:
    chan = AnalogIn(ads, ADS.P0, ADS.P1)
    currentSample = chan.voltage # the current voltage value as a float

    currentTime = time.time() - startTime
    if currentTime < 3.0 and initFlag:
        samples.append(currentSample)
    elif currentTime > 3.0 and initFlag:
        initFlag = False
        saveCSV(filename,samples)
        counterFlag = True
        samples.clear()
        print("\nInitial samples collected.\nIncrease the amperage 50 mA.\nPress the spacebar to collect 100 more samples.\n")

    if continueFlag:
        samples.append(currentSample)
        counter += 1
    
    if counter == 100:
        continueFlag = False
        counter = 0
        saveCSV((filename[:7] + "_" + str(fnCount) + filename[7:]), samples)
        fnCount += 1
        samples.clear()
        
    # creating a loop to check events that are occurring
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # checking if keydown event happened or not
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if continueFlag == False:
                    continueFlag = True