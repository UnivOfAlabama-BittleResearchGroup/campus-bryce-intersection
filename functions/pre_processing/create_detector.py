'''
create_detector.py is used to create SUMO (type e1) detectors at the locations of real-life detectors.

The inputs to the this tool are:
1. The .net.xml file of network the detectors are to be placed in.
2. The intersection_setup_file.xlsx file
    - Specifically the columns [ID], [Lane], [Sumo_Detector] & [Detector_Distance] are used

The outputs are:
1. detector.add.xml file in the format specified by SUMO
2. detector_params.txt
    - this file maps the sumo detectors to the lane it should control in the tls logic file.
        - Currently, the work flow is to generate this file and then copy paste into the tls logic file, as it is not
            autogenerated

This python module can be ran as a standalone file or called as a module by another python program
The default locations and names for the files are specified in the definitions.py file.

created by: Max Schrader
'''

import os
import sys
import numpy as np
from xml.dom import minidom
from functions.pre_processing import intersection_parameters
from global_config_parameters import CONFIG
import definitions as var_def
import sumolib  # noqa


def generate_xml(net_dir=CONFIG.net_file,
                 intersection_params=CONFIG.intersection_setup_file,
                 detect_file_path=CONFIG.detector,
                 tls_param_file_path=var_def.TLS_DETECT_TXT_FILE_ABSOLUTE,
                 detector_output_file_name=var_def.DETECTOR_OUTPUT_NAME,
                 detector_output_per_tls=False,
                 detector_output_path=var_def.DETECTOR_OUTPUT_DIR_RELATIVE,
                 freq='60'):

    """
    This function is used to generate the detector xml files. It uses the intersection params file and the net_dir to
    place the detectors their desired distance from the intersection.

    :param net_dir: the location and name of the net file
    :param intersection_params: the intersection setup file
    :param detect_file_path: the location+name of the detector.add.xml file
    :param tls_param_file_path: the location+name of the auxilary TXT file that can be used to help generate the dual
                                ring controller TLS files
    :param detector_output_file_name: the name of the file that the detectors should write to when the simulation runs.
    :param detector_output_per_tls: If there should be seperate detector output file per traffic light
    :param detector_output_path: the path to where the detector output file should be written.
    :param freq: the frequency at which the detector file should be written to by the simulation.

    :return: None
    """
    # read in the equivalencies
    equivy = intersection_parameters.IntersectionParameters()
    equivy.import_file(intersection_params)
    variable_df = equivy.df

    variable_df['Detect_Actual_Lane'] = variable_df.Lane.values
    variable_df['Detect_2_Actual_Lane'] = variable_df.Lane.values

    variable_df['Detect_Actual_Distance'] = variable_df.Detector_Distance.values
    variable_df['Detect_2_Actual_Distance'] = variable_df.Detector_2_Distance.values

    variable_df['Detect_Actual_Edge'] = variable_df.Edge.values
    variable_df['Detect_2_Actual_Edge'] = variable_df.Edge.values

    # read in the NET
    net = sumolib.net.readNet(net_dir)

    # create the XML docs
    doc = minidom.Document()
    doc_2 = minidom.Document()

    doc.appendChild(doc.createComment("Generated Detectors"))
    additional = doc.createElement('additional')
    doc.appendChild(additional)

    additional_2 = doc_2.createElement('additional')
    doc_2.appendChild(additional_2)

    for i in range(len(variable_df.Lane)):

        try:
            populated = not np.isnan(variable_df.Sumo_Detector[i])  # for handling blank primary detectors in the excel file
        except TypeError:
            populated = True

        if populated:

            param_element = doc_2.createElement('param')

            # this if statement is used to add seperators in the .txt file
            if i == 0:
                additional_2.appendChild(doc_2.createComment(str(variable_df.ID[i])))
            elif variable_df.ID[i] != variable_df.ID[max(i - 1, 0)]:
                additional_2.appendChild(doc_2.createComment(str(variable_df.ID[i])))

            param_element.setAttribute('key', variable_df.Lane[i])
            param_element.setAttribute('value', variable_df.Sumo_Detector[i])
            additional_2.appendChild(param_element)

        secondary_detector = equivy.get_secondary_detect(variable_df.Lane[i])

        if not secondary_detector:
            detector_list = [[variable_df.Sumo_Detector[i], variable_df.Detector_Distance[i]]]
            local_lane = [variable_df.Lane[i], ""]
        else:
            detector_list = [[variable_df.Sumo_Detector[i], variable_df.Detector_Distance[i]],
                             [secondary_detector, variable_df.Detector_2_Distance[i]]]
            local_lane = [variable_df.Lane[i], variable_df.Lane[i]]

        lane_index = 0

        if variable_df.Lane[i] == 'gneE51_0':
            x = 0

        for detect in detector_list:

            try:
                populated = not np.isnan(detect[0])  # for handling blank primary detectors in the excel file
            except TypeError:
                populated = True

            if populated:

                detect_element = doc.createElement('e1Detector')
                detect_element.setAttribute('id', detect[0])

                length = net.getLane(local_lane[lane_index]).getLength()
                # 1/3.28084 is the conversion from feet to meters
                offset = str(round(-1 * detect[1] / 3.28084, 1))
                # search backward via connecting lanes for a location the specified distance back
                while length < (detect[1] / 3.28084):
                    next_lane = net.getLane(local_lane[lane_index]).getIncoming()
                    local_lane[lane_index] = next_lane[0].getID()
                    offset = str(round(length - (variable_df.Detector_Distance[i] / 3.28084)))
                    length += net.getLane(local_lane[lane_index]).getLength()

                detect_element.setAttribute('pos', offset)
                detect_element.setAttribute('lane', local_lane[lane_index])
                detect_element.setAttribute('freq', freq)

                if detector_output_per_tls:
                    detect_element.setAttribute('file', detector_output_path + str(variable_df.ID[i]) +
                                                detector_output_file_name)
                else:
                    detect_element.setAttribute('file', detector_output_path + detector_output_file_name)

                additional.appendChild(detect_element)

                variable_df.loc[i, 'Detect_Actual_Lane'] = local_lane[0]
                variable_df.loc[i, 'Detect_2_Actual_Lane'] = local_lane[1]

                if lane_index == 0:
                    variable_df.loc[i, 'Detect_Actual_Distance'] = offset
                else:
                    variable_df.loc[i, 'Detect_2_Actual_Distance'] = offset

                lane_index += 1

                try:
                    variable_df.loc[i, 'Detect_Actual_Edge'] = net.getLane(local_lane[0]).getEdge().getID()

                    if local_lane[1]:
                        variable_df.loc[i, 'Detect_2_Actual_Edge'] = net.getLane(local_lane[1]).getEdge().getID()
                    else:
                        variable_df.loc[i, 'Detect_2_Actual_Edge'] = ""

                except KeyError or IndexError:
                    sys.exit("The Edge or Lane specified in the .xlsx does not exist in the .net.xml file")

    equivy.write_df(variable_df)
    equivy.write_to_excel(intersection_params)

    xml = doc.toprettyxml(indent='   ')
    f = open(detect_file_path, "w")
    f.write(xml)
    f.close()

    if tls_param_file_path is not None:
        # Write the detector equivalencies for the traffic light logic document
        xml_2 = doc_2.toprettyxml(indent='   ')
        f_2 = open(tls_param_file_path, "w")
        f_2.write(xml_2)
        f_2.close()

    print("Detectors generated successfully!")


if __name__ == '__main__':

    generate_xml(net_dir=CONFIG.net_file,
                 intersection_params=CONFIG.intersection_setup_file,
                 detect_file_path=CONFIG.detector,
                 tls_param_file_path=None,
                 detector_output_file_name=var_def.DETECTOR_OUTPUT_NAME,
                 detector_output_per_tls=False,
                 detector_output_path=var_def.DETECTOR_OUTPUT_DIR_RELATIVE,
                 freq='1')
