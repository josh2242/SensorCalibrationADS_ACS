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
count = 1
while(True):
    #print(chan.value, chan.voltage)
    for i in range(1000):
        voltage_value_list.append(chan.voltage)
    for v in voltage_value_list:
        total += v
    avg = total / len(voltage_value_list)
    voltage_average_list.append(avg)
    print(f"{count} Average: {avg}")
    voltage_value_list = []
    total = 0
    count = count + 1
    if count == 100:
        break
    
with open(filename, 'w') as file_object:
    file_object.write("Voltage\n")
    for av in voltage_average_list:
        file_object.write(str(av) + "\n")
