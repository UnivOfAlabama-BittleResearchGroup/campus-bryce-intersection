#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 14:39:57 2020

@author: max
"""

import os
import subprocess
import sys
import definitions as var_def
from global_config_parameters import CONFIG

RANDOM_TRIPS_PATH = os.path.join(os.environ['SUMO_HOME'], 'tools', 'randomTrips.py', )

ROUTE_UNVERIFIED_NAME = 'unverified_routes.xml'
FLOW_UNVERIFIED_NAME = "unverified_flow.xml"
ROUTE_FILE_NAME = "routes.xml"
FLOW_FILE_NAME = "trips.trips.xml"
FRINGE_FACTOR = '10'
LANE_FACTOR = '10'
MIN_DISTANCE = '50'

VEH_DISTR_FILE = CONFIG.veh_description
PERIOD = 3
SIM_LENGTH = str(3600)

def run(validate,
        period=PERIOD,
        net_file_path=CONFIG.net_file,
        output_file_path=os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, ROUTE_FILE_NAME),
        output_flow_path=os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, FLOW_FILE_NAME),
        sim_length=SIM_LENGTH,
        departspeed='max',
        vehicle_distro_file=VEH_DISTR_FILE,
        vehicle_class="vehDist",
        ):

    """
    This function calls the SUMO randomTrips.py module.

    :param output_flow_path:
    :param validate: if the routes should be validated or not
    :param period: the period between vehicle departures
    :param net_file_path: the net file
    :param output_file_path:
    :return:
    """

    departspeed_string = f'departSpeed="{departspeed}"'

    vehicle_class_string = f'type="{vehicle_class}"'

    trip_attribute_string = " ".join([departspeed_string, vehicle_class_string])

    #trip_attribute_string = departspeed_string

    if validate:
        subprocess.run([sys.executable, RANDOM_TRIPS_PATH,
                        "-n", net_file_path,
                        '--fringe-factor', FRINGE_FACTOR,
                        #'--additional-file', vehicle_distro_file,
                        '--route-file', output_file_path,
                        '-o', output_flow_path,
                        '-e', sim_length,
                        '--validate',   # This is the difference between validate and not
                        '-L', LANE_FACTOR,
                        '--min-distance', MIN_DISTANCE,
                        '--period', str(period),
                        '--trip-attributes', trip_attribute_string,
                        ])

    else:
        subprocess.run([sys.executable, RANDOM_TRIPS_PATH,
                        "-n", net_file_path,
                        '--fringe-factor', FRINGE_FACTOR,
                        #'--additional-file', vehicle_distro_file,
                        '--route-file', output_file_path,
                        '-o', output_flow_path,
                        '-L', LANE_FACTOR,
                        '-e', sim_length,
                        '--min-distance', MIN_DISTANCE,
                        '--period', str(period),
                        '--trip-attributes', trip_attribute_string,
                        ])


if __name__ == '__main__':

    run(validate=True)
