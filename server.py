import socket

import time

# cflib libraries
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper


# Radio connection address for CF
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E704') # Current CF in use is 04

HOST = '192.168.22.44' # Static IP of this laptop

PORT = 2242

#
#   Global Variables
#
isVerified = False  # GLOBAL
big_Text = '' # GLOBAL

#
#   Local Variables
#
isMainProcessing = False
isFreshPolygon = True
currentVextexCount = 0
j = 1
sTime = 0.0 # Time start
cTime = 0.0 # Time at confirmation
aTime = 0.0 # Time elapsed during algorithm

#
#   Parameter Functions
#
def param_stab_est_callback(name, value): # Executed when parameter setting is verified by CF
    global isVerified
    isVerified = True

def simple_param_async(scf, groupstr, namestr):
    cf = scf.cf
    cf.param.add_update_callback(group=groupstr, name=namestr, cb=param_stab_est_callback)

def send_data(scf, group, name, data):
    global isVerified, cTime, sTime
    full_name = group + '.' + name
    scf.cf.param.set_value(full_name, data)
    simple_param_async(scf,group,name)
    while(isVerified == False):                   # isVerified will not be triggered until CF verifies value change.
        continue
    cTime = time.time() - sTime
    isVerified = False

def read_data(scf, group, name):
    full_name = group + '.' + name
    val = scf.cf.param.get_value(full_name, timeout=5000)
    print(val)
    return val


#
#   Console logging functions. Any time new characters are recieved from the DEBUG on the CF,
#   they are appeneded to global variable big_text, which is handled at the end of the program.
#
def log_console(text):
    global big_Text
    big_Text = big_Text + text



#
#   Main loop.
#
if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()
    
    print("HOST - START")
    group = 'geofence'
    name = 'init'
    isMainProcessing = True
    i = 0                                           # Reset line index count
    print("Connected to CF!")
    print("Waiting for client to connect...")
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST,PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected to client by address {addr}!")
                print("Waiting for client to send READY...")
                while True:                                                     # Wait for client to send READY
                    data = conn.recv(1024)
                    if not data:
                        break
                    string_data = data.decode('utf-8')
                    if string_data == "READY":
                        print("Ready! Sending GO to CF!")
                        break
                conn.sendall(b"GO") # Send GO to client
                sTime = time.time()
                while isMainProcessing:
                    
                    # Initialize Geofence Algorithm on CF
                    send_data(scf,group,name,1)

                    print("Waiting for CF to finish...")
                    while True:                         # wait until STOP flag is set on CF
                        value = read_data(scf,group,'stop')
                        if value != "0":
                            aTime = time.time() - sTime
                            break
                        scf.cf.console.receivedChar.add_callback(log_console)       # Print CF DEBUG messages
                        continue 
                    conn.sendall(b"STOP")                                           # Send STOP to client
                    
                    print("Algorithm complete!")
                    while True: 
                        valueF = read_data(scf,group,'totalTime')                  # wait until final time is recieved by CF
                        if valueF != "0.0":
                            break
                        scf.cf.console.receivedChar.add_callback(log_console)       # Print CF DEBUG messages
                        continue 
                    scf.cf.console.receivedChar.add_callback(log_console)         # Print CF DEBUG messages
                    isMainProcessing = False
                #print(big_Text)
                #print(f"Start time: {sTime}")
                print(f"Confirmation HOST time: {cTime}")
                print(f"Algorithm Host time: {aTime}\n\n")
                conn.sendall(bytes(str(cTime), 'utf-8'))
                conn.sendall(bytes(str(aTime), 'utf-8'))
    # Write output file of HOST
    with open('HOST Times and DEBUG.txt', 'w') as file_object:
        file_object.write(f"CF Time Elapsed: {valueF}\n")
        file_object.write(f"Confirmation Host time: {cTime}\n")
        file_object.write(f"Algorithm Host time: {aTime}\n")
        for line in big_Text:
            file_object.write(line)
            
    print("HOST - END")



# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST,PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print(f"Connected by {addr}")
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             string_data = data.decode('utf-8')
#             if string_data == "One":
#                 print("Got 1!")
#                 break
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             string_data = data.decode('utf-8')
#             if string_data == "Two":
#                 print("Got 2!")
#                 break
#         conn.sendall(b"STOP")