import board
import busio
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

chan = AnalogIn(ads, ADS.P2, ADS.P3)

voltage_value_list = []
voltage_average_list = []

filename = "Voltage_Calib.csv"

total = 0
count = 0
while(True):
    #print(chan.value, chan.voltage)

    print(chan.voltage)
