from __future__ import absolute_import
from __future__ import print_function

import os
import sys
from functions.traffic_lights.traffic_light_manager import TrafficLightManager
import time
# %% Import Traci
from sumolib import checkBinary  # noqa
import traci  # noqa


class TraciWRealWorldTrafficLights:

    def __init__(self,
                 gui,
                 rw_data,
                 rw_start_time,
                 sim_length,
                 sim_step,
                 traffic_light_phasing,
                 traffic_light_ids,
                 # changing_params,
                 # sumocfg,
                 sumo_string):

        """

        :param gui: display simulation in the GUI or not
        :param rw_data: the rw_data_dict
        :param rw_start_time: the simulation start time
        :param sim_length: the simulation length in seconds
        :param sim_step: the simulation step
        :param traffic_light_phasing: the traffic light phasing document
        :param traffic_light_ids: the traffic light ids
        :param sumo_string: the sumo cmd line string
        """

        self.sumo_string = sumo_string
        self.rw_start_time = rw_start_time
        self._sumoBinary = None
        self._traffic_light_manager = None
        self._step = sim_step
        self._length = sim_length
        self._tl_phasing = traffic_light_phasing
        self._rw_data = rw_data
        self._tl_ids = traffic_light_ids
        self._gui = gui

    def initialize(self):

        self._traffic_light_manager = TrafficLightManager(end_time=self._length,
                                                          traffic_light_phasing=self._tl_phasing,
                                                          rw_start_time=self.rw_start_time,
                                                          rw_csv_data=self._rw_data,
                                                          traffic_light_ids=self._tl_ids
                                                          )

        if self._gui:

            self._sumoBinary = checkBinary('sumo-gui')

        else:

            self._sumoBinary = checkBinary('sumo')

        # traci.start([self._sumoBinary, "-c", self.sumocfg, "--step-length", str(self._step)])
        traci.start([self._sumoBinary] + self.sumo_string)

    def run(self):

        self.initialize()

        change_time = None

        while traci.simulation.getTime() < self._length:

            if (traci.simulation.getTime() + self._step) > self._traffic_light_manager.convert_from_datetime(
                    date_time=change_time):

                tl_dict, change_time = self._traffic_light_manager.get_light_string(
                    sim_time=traci.simulation.getTime(),
                    step_time=self._step
                )
                for key in tl_dict:
                    traci.trafficlight.setRedYellowGreenState(key, tl_dict[key]['light_string'])
                    traci.trafficlight.setPhaseName(key, tl_dict[key]['phase_name'])

            traci.simulationStep()

        traci.close()
        sys.stdout.flush()
