import os
import sys
import time
import definitions as var_def
from global_config_parameters import CONFIG
from functions.pre_processing.intersection_parameters import IntersectionParameters
from sumolib import checkBinary  # noqa
import traci  # noqa
from pysnmp.hlapi import *

gui = True

if gui:

    sumoBinary = checkBinary('sumo-gui')

else:

    sumoBinary = checkBinary('sumo')

    # traci.start([sumoBinary, "-c", self.sumocfg, "--step-length", str(step)])

SIM_LENGTH = CONFIG.sim_length
IP = "127.0.0.1"
PORT = 501


def run(rw_index):

    # detector_ids = traci.lanearea.getIDList()

    while traci.simulation.getTime() < SIM_LENGTH:
        t0 = time.time()

        hex_string = get_occupancy(IDS=rw_index)

        if hex_string is not None:
            send_detectors(hex_string)

        # sim step
        traci.simulationStep()

        # sleep enough to make sim step take 1 second (real-time)
        dt = (time.time() - t0)
        time.sleep(max(CONFIG.sim_step - dt, 0))

    traci.close()
    sys.stdout.flush()


def get_occupancy(IDS):

    binary_list = ["0"] * 8

    for i, ID in enumerate(IDS[0]):
        if traci.lanearea.getLastStepOccupancy(ID) > 0.01:
            binary_list[8 - int(IDS[1][i])] = "1"
            print(f"Call to detector {IDS[1][i]}")

    detect_on = "".join(binary_list)

    if "1" in detect_on:
        print(detect_on)
        print('%0*X' % ((len(detect_on) + 3) // 4, int(detect_on, 2)))
        return '%0*X' % ((len(detect_on) + 3) // 4, int(detect_on, 2))
    else:
        return None

def send_detectors(hex_string):

    next(
        setCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((IP, PORT)),
               ContextData(),
               ObjectType(ObjectIdentity('1.3.6.1.4.1.1206.3.5.2.19.8.2.1'), OctetString(hexValue=hex_string))
               )
    )


def index_detectors(intersection_setup_file):

    parameters = IntersectionParameters()
    parameters.import_file(intersection_setup_file)

    # this won't work with more than 1 traffic light
    rw_index = parameters.get_rw_index_by_light(CONFIG.tl_ids[0], main=True, dict=False)

    return rw_index


if __name__ == "__main__":

    rw_index = index_detectors(intersection_setup_file=CONFIG.intersection_setup_file)

    command_line_list = CONFIG.get_cmd_line_list(method='randomRoutes',
                                                 sim_length=CONFIG.sim_length,
                                                 sim_step=CONFIG.sim_step,
                                                 emissions=False,
                                                 dual_ring_lights=False)

    traci.start([sumoBinary] + command_line_list)

    run(rw_index)