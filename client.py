import socket
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

chan1 = AnalogIn(ads, ADS.P0, ADS.P1)       # Current Sensor readings
chan2 = AnalogIn(ads, ADS.P2, ADS.P3)       # Battery voltage readings

# def saveCSV(filename, float_list):
#     """Saves a CSV given the filename and list of values."""
#     with open(filename, 'w') as file_object:
#         for value in float_list:
#             file_object.write(str(value) + "\n")
#     print(f"{filename} has been saved.")


filename = "Results.csv"

HOST = '192.168.22.44'
PORT = 2242

voltageCount = 0
sTime = 0.0
stopTime = 0.0

continueFlag = False

print("Client - START")

with open(filename, 'w') as file_object:
    file_object.write("TIME,VOLTAGE,CURRENT\n")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        print("Connected")
        # Wait for 100 readings of sub 4.08 V
        if chan2.voltage < 4.08:
            print("Wait for 100 readings of sub 4.08 V...")
        else:
            print("Above 4.08 V ...")
        while True:
            if chan2.voltage < 4.08:
                voltageCount = voltageCount + 1
            if voltageCount > 100:
                print("Voltage at just below 4.08 V")
                break
        
        s.sendall(b"READY")

        # Wait for HOST to send GO
        print("Waiting for HOST to send GO...")
        while True:
            data = s.recv(1024)
            if not data:
                break
            string_data = data.decode('utf-8')
            if string_data == "GO":
                print(f"Recieved {string_data} command.\nGathering data until STOP command...")
                break
        
        # Data collection begins at sTime
        sTime = time.time()
        print("Waiting to finish...")
        file_object.write(str((time.time())-sTime) + "," + str(chan2.voltage) + "," + str(chan1.voltage) + "\n")
        while True:
            try:
                data = s.recv(1024, socket.MSG_DONTWAIT)
                string_data = data.decode('utf-8')
                continueFlag = True
            except BlockingIOError:
                pass                    
            if not data:
                break
            if string_data == "STOP":               # Kill data collection after STOP
                print(f"Recieved {string_data} command")
                break
            file_object.write(str((time.time())-sTime) + "," + str(chan2.voltage) + "," + str(chan1.voltage) + "\n")
        stopTime = (time.time()) - sTime
        file_object.write(f"Total elapsed time on Client: {str(stopTime)}\n")
        #Get data from HOST
        #while True:
        #    data = s.recv(4096, socket.MSG_WAITALL)
        #    if not data:
        #        print("Not data... D:")
        #        break
        #    string_data = data.decode('utf-8')
        #    file_object.write(f"Confirmation time on HOST: {string_data}\n")
        #    break
        #while True:
        #    data = s.recv(4096, socket.MSG_WAITALL)
        #    if not data:
        #        print("Not data... D:")
        #        break
        #    string_data = data.decode('utf-8')
        #    file_object.write(f"Total elapsed time on HOST: {string_data}")
        #    break


print(f"\n\nClient - END.")
