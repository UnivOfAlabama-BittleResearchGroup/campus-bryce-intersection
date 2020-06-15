'''
definitions.py is the master file definition file for the project. These locations are imported into all of the scripts

ROOT is automatically set to the working directory aka it solves the absolute vs. relative path problem
'''

import os
import sys

# add SUMO_HOME/tools to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


ROOT = os.path.dirname(os.path.abspath(__file__))

SIM_FILES_ABS = os.path.join(ROOT, 'sim_files')

NET_FILE_DIR_ABSOLUTE = os.path.join(SIM_FILES_ABS, 'net')

DETECT_DIR_ABS = os.path.join(SIM_FILES_ABS, 'detectors')

INTERSECTION_SETUP_FILE_NAME = 'intersection_setup_file.xlsx'
TRAFFIC_LIGHT_STATE_DESCRIPT = 'traffic_light_phasing.xlsx'
INTERSECTION_PARAMETERS_ABS = os.path.join(ROOT, 'intersection_parameters')

INTERSECTION_SETUP_FILE_ABSOLUTE = os.path.join(INTERSECTION_PARAMETERS_ABS, INTERSECTION_SETUP_FILE_NAME)
TRAFFIC_LIGHT_STATE_DESCRIPTION_ABSOLUTE = os.path.join(INTERSECTION_PARAMETERS_ABS, TRAFFIC_LIGHT_STATE_DESCRIPT)

SIM_INPUTS_RELATIVE = ""  # There should be no / proceeding the first sub folder
SIM_INPUTS_ABSOLUTE = os.path.join(ROOT, 'sim_files')

# Detector Files
DETECT_FILE_NAME = 'detector.add.xml'
DETECT_DIR_RELATIVE = os.path.join(SIM_INPUTS_RELATIVE, 'detectors')
DETECT_FILE_RELATIVE = os.path.join(DETECT_DIR_RELATIVE, DETECT_FILE_NAME)
DETECT_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, DETECT_DIR_RELATIVE)
DETECT_FILE_ABSOLUTE = os.path.join(DETECT_DIR_ABSOLUTE, DETECT_FILE_NAME)
DETECTOR_OUTPUT_NAME = '_detect_OUTPUT_.xml'
DETECTOR_OUTPUT_DIR_RELATIVE = ''
DETECTOR_OUTPUT_FILE_ABSOLUTE = os.path.join(DETECT_DIR_ABSOLUTE, DETECTOR_OUTPUT_NAME)

# Calibrator Files
CALIBRATOR_FILE_NAME = 'calibrator.xml'
CALIBRATOR_DIR_RELATIVE = os.path.join(SIM_INPUTS_RELATIVE, 'calibrators')
CALIBRATOR_FILE_RELATIVE = os.path.join(CALIBRATOR_DIR_RELATIVE, CALIBRATOR_FILE_NAME)
CALIBRATOR_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, CALIBRATOR_DIR_RELATIVE)
CALIBRATOR_FILE_ABSOLUTE = os.path.join(CALIBRATOR_DIR_ABSOLUTE, CALIBRATOR_FILE_NAME)
CALIBRATOR_OUTPUT_NAME = '/dev/null'  # '_calibrator_OUTPUT_.xml'
CALIBRATOR_OUTPUT_RELATIVE = ''  # calibrator output files don't observe relative paths.

PROBE_FILE_NAME = 'probe.xml'
PROBE_DIR_RELATIVE = os.path.join(SIM_INPUTS_RELATIVE, 'calibrators')
PROBE_FILE_RELATIVE = os.path.join(PROBE_DIR_RELATIVE, PROBE_FILE_NAME)
PROBE_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, PROBE_DIR_RELATIVE)
PROBE_FILE_ABSOLUTE = os.path.join(PROBE_DIR_ABSOLUTE, PROBE_FILE_NAME)
PROBE_OUTPUT_NAME = '/dev/null'  # set to 'NULL' if no output is desired
PROBE_OUTPUT_RELATIVE = ''

TLS_LOGIC_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, 'tl_logic')
TLS_DETECT_TXT_FILE_ABSOLUTE = os.path.join(TLS_LOGIC_DIR_ABSOLUTE, 'detector_params.txt')
TLS_STATE_OUTPUT_FILE_ABSOLUTE = os.path.join(TLS_LOGIC_DIR_ABSOLUTE, 'tls_state_OUTPUT_.xml')

DECAL_FILE_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, 'decal')

EMISSIONS_DIR_ABS = os.path.join(SIM_INPUTS_ABSOLUTE, 'emissions')
EMISSIONS_OUTPUT_FILE_ABS = os.path.join(EMISSIONS_DIR_ABS, "_OUTPUT_emissions.xml")

SIM_OUTPUT_DATA_DIR = os.path.join(ROOT, 'sim_output_data')


FCD_OUTPUT_DIR_ABS = os.path.join(SIM_INPUTS_ABSOLUTE, 'fcd_output')
FCD_OUTPUT_FILE_ABS = os.path.join(FCD_OUTPUT_DIR_ABS, '_OUTPUT_fcd.xml')

TRIP_INFO_OUTPUT_DIR_ABS = os.path.join(SIM_INPUTS_ABSOLUTE, 'trip_info_output')
TRIP_INFO_OUTPUT_FILE_ABS = os.path.join(TRIP_INFO_OUTPUT_DIR_ABS, '_OUTPUT_trip_info.xml')

FLOW_ROUTE_DIR_RELATIVE = os.path.join(SIM_INPUTS_RELATIVE, 'flow_routes')
FLOW_ROUTE_DIR_ABSOLUTE = os.path.join(SIM_INPUTS_ABSOLUTE, FLOW_ROUTE_DIR_RELATIVE)