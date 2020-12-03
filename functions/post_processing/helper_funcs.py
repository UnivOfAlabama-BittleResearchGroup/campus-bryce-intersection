"""
This module contains various functions for post processing simulation detectors and traffic light output files.
It also gets the rw detector counts and handles the standard file locations.

"""


import os
import sys

import pandas as pd

import definitions as var_def
from global_config_parameters import CONFIG
# from functions.SQL.rw_traffic_data import RWTrafficData
from functions.post_processing import xml_parse

"""This statement below is necessary if using SUMOs xml2csv converter"""
# # adding the location of sumo/tools/xml to the path
# if 'SUMO_HOME' in os.environ:
#     tools = os.path.join(os.environ['SUMO_HOME'], 'tools', 'xml')
#     sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

# importing the sumo tool for converting the .xml outputs to .csv
# import xml2csv

# getting the parameters defined in the global_simulation_parameters


# set a default excel file name
excel_file_name = 'dual_ring_output.xlsx'

# set the default file locations
SQL_FILE = CONFIG.rw_data_csv
SUMO_DETECTOR_FILE = CONFIG.detector_output_file
TLS_FILE_NAME = CONFIG.tl_output_file
TLS_CSV_NAME = os.path.join(var_def.SQL_DATA_DIR_ABSOLUTE, "tls_state_OUTPUT_.csv")
DETECT_CSV_NAME = os.path.join(var_def.SQL_DATA_DIR_ABSOLUTE, "_detect_OUTPUT_.csv")
EXCEL_FILE_NAME = os.path.join(var_def.SQL_DATA_DIR_ABSOLUTE, excel_file_name)


def convert_xml(sumo_detector_file=SUMO_DETECTOR_FILE, detect_csv_name=DETECT_CSV_NAME,
                tls_file_name=TLS_FILE_NAME, tls_csv_name=TLS_CSV_NAME):

    """
    This function converts the SUMO outputs as a .xml to .csv files

    :param sumo_detector_file: the sumo detector file output
    :param detect_csv_name: the .csv file to write the converted sumo detector file to
    :param tls_file_name: the tls output file name
    :param tls_csv_name: the .csv file to write the converted tls output file name

    :return:
    """

    if sumo_detector_file is not None:
        xml_parse.parse_detector_xml(sumo_detector_file, detect_csv_name)
        # xml2csv.main([sumo_detector_file, '-o', detect_csv_name, '-s', ','])
    if tls_file_name is not None:
        xml_parse.parse_tl_xml(tls_file_name, tls_csv_name)
        # xml2csv.main([tls_file_name, '-o', tls_csv_name, '-s', ','])


def read_csv(detect_csv_name=DETECT_CSV_NAME, tls_csv_name=TLS_CSV_NAME):
    """
    This function is used to read in the csv files as pandas dataframe

    :param detect_csv_name:
    :param tls_csv_name:
    :return: detector Pandas DataFrame, traffic_light Pandas DataFrame
    """

    # Read in the csv files from simulation
    if detect_csv_name is not None:
        detector_df = pd.read_csv(detect_csv_name, dtype={'interval_end': float})
    else:
        detector_df = None

    if tls_csv_name is not None:
        tls_df = pd.read_csv(tls_csv_name)
        return detector_df, tls_df

    else:
        return detector_df


def get_rw_detector_counts(rw_csv_file=SQL_FILE, tl_ids=None):
    """
    This function makes the call to the RWTrafficData class and process the SQL csv file

    :param rw_csv_file:
    :param tl_ids:
    :return: dict(tl_id: Pandas DataFrame)
    """

    if tl_ids is None:
        tl_ids = RWTrafficData(file_path=rw_csv_file).get_unique_tl_ids()

    rw_detector_data = RWTrafficData(file_path=rw_csv_file).detector_events.get_on_counts(tl_ids)

    return rw_detector_data


def to_excel(detector_df, tls_df, rw_detector_dict, excel_name=EXCEL_FILE_NAME):
    """
    writes the parameters to an excel file.

    :param detector_df:
    :param tls_df:
    :param rw_detector_dict:
    :param excel_name:
    :return: None
    """
    writer = pd.ExcelWriter(excel_name)
    detector_df.to_excel(writer, sheet_name='Detectors')
    tls_df.to_excel(writer, sheet_name='TLS')

    for tl_id in rw_detector_dict.keys():

        pd.DataFrame(rw_detector_dict[tl_id]).to_excel(writer, sheet_name=tl_id + '_rw_detectors')

    writer.save()

#def read_detector_output():

