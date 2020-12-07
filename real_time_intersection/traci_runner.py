import os
import sys
import time
import glob
import subprocess
import definitions
import pandas as pd
from datetime import datetime, timedelta
from global_config_parameters import CONFIG
from functions.pre_processing.intersection_parameters import IntersectionParameters
from sumolib import checkBinary  # noqa
import traci  # noqa
from functions.real_time_lights.sumo_info_process import DetectorProcess
from functions.real_time_lights.snmp import SNMP
from functions.real_time_lights.tl_fsm import SILLightManager
from functions.read_detector_xml import ParseDetectorXML

gui = True
if gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')

IP = "127.0.0.1"
PORT = 501

HIGH_RES_TRANSLATOR_PATH = r'C:\Users\spraychamber\Max\Virtual_Traffic_Light\HighResTranslator 3.1.0.6\HighResTranslator\HighResTranslator.exe'
ASC3_OUTPUT_PATH = r'C:\Users\spraychamber\Max\Virtual_Traffic_Light\12.66.30'


def process_asc3_output(start_datetime, end_datetime):
    # getting the .datZ files:
    datZ_files = []
    file_names = []
    for file in glob.glob(f"{ASC3_OUTPUT_PATH}\*.datZ"):
        file_names.append(os.path.split(file)[-1])
    file_names.sort()
    for i, file_name in enumerate(file_names):
        file_end_list = file_name.split('_')[2:]
        file_end_time = datetime(year=int(file_end_list[0]), month=int(file_end_list[1]), day=int(file_end_list[2]),
                                 hour=int(file_end_list[3].split('.')[0][:2]), minute=int(file_end_list[3].split('.')[0][2:]))
        if (file_end_time + timedelta(minutes=15)) > end_datetime:
            datZ_files.append(file_name)
            if file_end_time > start_datetime:
                datZ_files.append(file_names[i-1])

    if datZ_files:
        for file in datZ_files:
            subprocess.check_output([HIGH_RES_TRANSLATOR_PATH, os.path.join(ASC3_OUTPUT_PATH, file)])
            new_file_name = '.'.join(file.split('.')[:-1] + ['csv'])
            os.rename(os.path.join(definitions.ROOT, 'real_time_intersection', new_file_name),
                      os.path.join(definitions.ROOT, 'econolite_logs', new_file_name))
        return datZ_files
    else:
        print('waiting on asc3 data to be saved...')
        time.sleep(60)
        # recursion! yay!
        return process_asc3_output(start_datetime, end_datetime)


def decode_hex(hex):
    binary = "{0:08b}".format(int(hex, 16))
    return binary


def run(sim_length, detector_rw_index, snmp_client, tl_manager):
    detector_processor = DetectorProcess(traci=traci, IDS=detector_rw_index)
    sim_time = 0
    light_states = []
    detector_states = []
    start_time = datetime.now()
    # snmp_client.set_recording('enable')
    while sim_time < sim_length:
        t0 = time.time()
        hex_string = detector_processor.get_occupancy()
        # step_time = (start_time + timedelta(seconds=float(sim_time))).strftime('%Y-%m-%d %H:%M:%S.%f')
        step_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        if hex_string:
            snmp_client.send_detectors(hex_string)
            detector_states.append([step_time, decode_hex(hex_string)])
        state_dict = snmp_client.get_light_states()
        tl_dict = tl_manager.get_light_strings(state_dict=state_dict, sim_time=sim_time)
        for item in tl_dict.items():
            if item[1]:
                traci.trafficlight.setRedYellowGreenState(item[0], item[1]['data'])
                light_states.append([step_time, item[0], item[1]['name']])
        # sim step
        traci.simulationStep()
        sim_time += CONFIG.sim_step
        # sleep enough to make sim step take 1 second (real-time)
        dt = (time.time() - t0)
        time.sleep(max(CONFIG.sim_step - dt, 0))
    end_time = datetime.now()
    print(end_time)
    snmp_client.kill_threads()  # want to cleanly kill the threads that are running i
    traci.close()
    sys.stdout.flush()
    return start_time, end_time, light_states, detector_states


def index_detectors(intersection_setup_file):
    parameters = IntersectionParameters()
    parameters.import_file(intersection_setup_file)
    # this won't work with more than 1 traffic light
    rw_index = parameters.get_rw_index_by_light(CONFIG.tl_ids[0], main=True, dict=False)
    return rw_index


def dump_light_states(light_state_list):
    import csv
    # opening the csv file in 'a+' mode
    file = open(os.path.join(definitions.TLS_LOGIC_DIR_ABSOLUTE, 'light_state.csv'), 'w+', newline='')
    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(light_state_list)


def dump_detector_logs(detector_list):
    import csv
    # opening the csv file in 'a+' mode
    file = open(os.path.join(definitions.DETECT_DIR_ABS, 'detector_states_tl.csv'), 'w+', newline='')
    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(detector_list)


if __name__ == "__main__":


    detect_rw_index = index_detectors(intersection_setup_file=CONFIG.intersection_setup_file)

    CONFIG.sim_length = 300

    CONFIG.sim_step = 0.5

    command_line_list = CONFIG.get_cmd_line_list(method='randomRoutes',
                                                 sim_length=CONFIG.sim_length,
                                                 sim_step=CONFIG.sim_step,
                                                 emissions=False,
                                                 dual_ring_lights=False)

    sil_tl_manager = SILLightManager(CONFIG.intersection_phasing_file)

    traci.start([sumoBinary] + command_line_list)

    snmp_client = SNMP(ip=IP, port=PORT, light_control=True)

    start_dt, end_dt, light_states, detector_states = run(CONFIG.sim_length, detect_rw_index, snmp_client, sil_tl_manager)

    file_list = process_asc3_output(start_datetime=start_dt, end_datetime=end_dt)

    dump_light_states(light_states)

    dump_detector_logs(detector_states)

    df = ParseDetectorXML().main(file_path=CONFIG.detector_output_file, save_path=None, detect_type='e2')

    df['interval_begin_dt'] = df['interval_begin'].apply(lambda x: start_dt + timedelta(seconds=float(x)))

    df.to_csv(".".join([CONFIG.detector_output_file.split('.')[0]] + ['csv']))


