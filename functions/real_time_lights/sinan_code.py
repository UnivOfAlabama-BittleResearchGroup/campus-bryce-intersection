import os
import getopt
import sys
import re
import time
import subprocess
from datetime import datetime  # import a libary to get current date and time

argv = sys.argv[1:]

ip_port = "501"
econolite = 0
scale = 16

try:
    opts, args = getopt.getopt(argv, "ha:p:e", ["addr=", "port="])
except getopt.GetoptError:
    print('%s -a <ip_address>' % (sys.argv[0]))
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print('%s -a <ip_address>' % (sys.argv[0]))
        sys.exit()
    elif opt in ("-a", "--addr"):
        ip_addr = arg
    elif opt in ("-p", "--port"):
        ip_port = arg
    elif opt in "-e":
        econolite = 1
    else:
        assert False, "unhandled option"

ip_addr = '127.0.0.1'
econolite=1

Phase = ['R'] * 9
Detection = [' '] * 65
# Detection = "X" * 65

red = 0

# New variable to keep track of previous phases, then we update it once its changed
previousPhase = 'init'

# for i in range(0,100):


while (1):
    # get the green and yellow status, assume phase is red
    green = yellow = 0
    Phase = ['R'] * 9
    cmd_g = "snmpget -v 1 -c public " + ip_addr + ":" + ip_port + " 1.3.6.1.4.1.1206.4.2.1.1.4.1.4.1"
    cmd_y = "snmpget -v 1 -c public " + ip_addr + ":" + ip_port + " 1.3.6.1.4.1.1206.4.2.1.1.4.1.3.1"
    returned_value_g = subprocess.check_output(cmd_g, shell=True)
    returned_value_y = subprocess.check_output(cmd_y, shell=True)
    # status_g = returned_value_g.rsplit(':', 1)
    # status_y = returned_value_y.rsplit(':', 1)
    # bits_g = bin(int(status_g[1].strip()))[2:].zfill(8)
    # bits_y = bin(int(status_y[1].strip()))[2:].zfill(8)
    # green = (str(red | int(bits_g)).zfill(8))[::-1]
    # yellow = (str(red | int(bits_y)).zfill(8))[::-1]
    # for j in range(1, 9):
    #     if (green[j - 1] == '1'):
    #         Phase[j] = 'G'
    #     if (yellow[j - 1] == '1'):
    #         Phase[j] = 'Y'

    # get detector status
    # is this an econolite controller
    #   OID returns 120 bytes of data, we only care about the first 8 bytes (64 bits)
    #   that gives us the 64 detectors, bit values are stored in Detection array, locations 1-64
    if (econolite == 1):
        cmd = "snmpget -v 1 -c public " + ip_addr + ":" + ip_port + " 1.3.6.1.4.1.1206.3.5.2.19.8.2.1"
        returned_value = subprocess.check_output(cmd, shell=True)
        status = str(returned_value).rsplit(':', 1)
        bytes = status[1].split(' ')
        for j in range(1, 9):
            bits = bin(int(bytes[j], scale))[2:].zfill(8)[::-1]
            for k in range(0, 8):
                Detection[(k + 8 * (j - 1)) + 1] = bits[k]
    # not an econolite controller
    #   if we can use the public detector storage location
    #   we need the first 8 bytes (64 bits - 64 detectors), make 8 calls
    #   store detector values in Detection array, locations 1-64
    else:
        for j in range(1, 9):
            cmd = "snmpget -v 1 -c public " + ip_addr + ":" + ip_port + " 1.3.6.1.4.1.1206.4.2.1.2.4.1.2." + str(j)
            returned_value = subprocess.check_output(cmd, shell=True)
            status = returned_value.rsplit(':', 1)
            bits = bin(int(status[1].strip()))[2:].zfill(8)
            for k in range(0, 8):
                Detection[(k + 8 * (j - 1)) + 1] = bits[k]

    # clear screen and print results
    time.sleep(1)
    # subprocess.call('cls' if os.name == 'nt' else 'clear')

    # get time from controller
    cmd = "snmpget -v 1 -c public " + ip_addr + ":" + ip_port + " 1.3.6.1.4.1.1206.4.2.6.3.1.0"
    returned_value = subprocess.check_output(cmd, shell=True)
    epoch = str(returned_value).rsplit(':', 1)
    print(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(float(epoch[1].strip("'").strip('\\n').strip('\\r')))))

    print("IP Address: " + ip_addr + " Port: " + ip_port)
    print("Phase")
    for j in range(1, 9):
        print('%d [%c]\t' % (j, Phase[j])),
    print('\n')

    # Check if this is the first time the program run
    # If it is the first time, then there is no previous phase, and previous phase = current phase
    # with open('notifications.txt', 'a') as f:
    #     if (previousPhase == 'init'):
    #         previousPhase = Phase
    #         f.write('\n')  # print a new line in the file
    #         f.write(str(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(
    #             float(epoch[1].strip())))))  # print the current machine's date and time of the initial phase in a file
    #         f.write(' ')  # add an empty space between time and phase xx yy
    #         # for item in Phase: #Print every item from the phase in the file
    #         for i in range(1, 9):
    #             f.write(Phase[i])
    #             print(Phase[i]),  ###
    #     else:  # If the program has ran before
    #         if (
    #                 previousPhase != Phase):  # Check if the previous phase = current phase ... if they don't equal, that means phase changed and write to file
    #             # with open('notifications.txt', 'a') as f: #open a new file and give it a name notifications.txt
    #             f.write('\n')  # print a new line in the file
    #             # f.write(str(datetime.now())) #print the current date and time in the file
    #             f.write(str(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(
    #                 float(epoch[1].strip())))))  # print MachineTime for any new phase
    #             f.write('\n')
    #             for j in range(1, 9):
    #                 for k in range(1, 9):
    #                     f.write('%02d %c\t' % ((k + 8 * (j - 1)), Detection[k + 8 * (j - 1)]))
    #                 f.write('\n')
    #             f.write(' ')  # add an empty space between time and phase xxx yyyy
    #             print(' '),  # print horiantally with space
    #             # for item in Phase: #Print every item from the phase in the file ++
    #             #  f.write(item) ++
    #             for i in range(1, 9):  # ---
    #                 if (str(previousPhase[i]) == str(Phase[i])):  # ---
    #                     f.write('-')  # ---
    #                     print('_'),  # print horizantally with space
    #                 else:  # ---
    #                     f.write(Phase[i])  # ---
    #                     print(Phase[i]),  ### print horizantally with space
    #             previousPhase = Phase
    # print('\n')
    # print("Detection")

    for j in range(1, 9):
        for k in range(1, 9):
            print('%02d %c\t' % ((k + 8 * (j - 1)), Detection[k + 8 * (j - 1)])),
        print(' ')