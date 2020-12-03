import os
import sys
import time
import definitions
from sumolib import checkBinary  # noqa
import traci  # noqa


# This is where PATH to SUMO is found
gui = True
if gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')


SIM_LENGTH = 300
STEP_LENGTH = 0.1

def run(sim_length, sim_step, real_time=True):
    sim_time = 0

    # snmp_client.set_recording('enable')
    while sim_time < sim_length:
        t0 = time.time()  # get the time before taking an action:

        """---------------- Take Action Here ------------------"""
        try:
            traci.vehicle.setColor('3', (255, 0, 0))  # set the vehicle color to red
            speed = traci.vehicle.getSpeed('3')
            print(f"Time: {sim_time} \t Speed: {speed}")
        except traci.exceptions.TraCIException:
            print('vehicle not in the network')
        """----------------------------------------------------"""

        sim_time += sim_step  # increment the sim_time
        dt = (time.time() - t0)  # find the time that the actions took to execute
        # This forces SUMO to run in real-time wait the step time - time that actions took to execute to
        if real_time:
            time.sleep(max(sim_step - dt, 0))
        # Step the simulation
        traci.simulationStep()

    traci.close()
    sys.stdout.flush()
    return


if __name__ == "__main__":

    # These are the parameters that are passed to SUMO
    command_line_list = ['-n', os.path.join(definitions.NET_FILE_DIR_ABSOLUTE, 'net.net.xml'),  # defines the network
                         '-r', os.path.join(definitions.FLOW_ROUTE_DIR_ABSOLUTE, 'routes.xml'), # defines each vehicles' routes
                         '-a', ', '.join([os.path.join(definitions.VEH_DESCRIPT_DIR_ABSOLUTE, 'vTypeDistributions.add.xml'),   # defines the vehicle type distribution (not really necessary)
                         os.path.join(definitions.DETECT_DIR_ABS, 'e2detect.add.xml')]),  # defines the detector file (not really necessary)
                         '-e', str(SIM_LENGTH),
                         '--step-length', str(STEP_LENGTH)]

    # start (open) SUMO
    traci.start([sumoBinary] + command_line_list)

    # run the simulation
    run(SIM_LENGTH, STEP_LENGTH, real_time=True)
