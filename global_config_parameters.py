import definitions as var_def
import os
import json
from datetime import datetime


class CONFIG:
    # """
    # The CONFIG class serves as a sort of master configuration file. A class was used so that the hierarchy can be
    # maintained.
    #
    # This class will be called in many of the python scripts and prevents having to change filename is multiple
    # locations if a filename is changed.
    #
    # It is also used to keep the filenames and locations consistent across the workflow
    # """

    # is the sumo gui desired for simulation? (Certain scripts might override this setting
    sumo_gui = True

    # # The desired upper and lower time bounds for the simulation. Should align with the simulation length.
    # # should always be in this format:
    # lower_time_bound = '02/05/2020 06:00:00.000'
    # upper_time_bound = '02/05/2020 10:00:00.000'
    # # the location of the RW data
    # rw_data_csv = os.path.join(var_def.SQL_DATA_DIR_ABSOLUTE, '2020-02-05.csv')

    sim_length = 4 * 3600  # seconds
    sim_step = 0.1  # seconds
    #tl_ids = ['63069006', '63069007', '63069008', '63069009']
    tl_ids = ['tl_1']
    aggregation_period = 60
    detector_output_freq = 5

    # the location and name of the network file, detector, calibrator and probe files
    net_file = os.path.join(var_def.NET_FILE_DIR_ABSOLUTE, 'net.net.xml')
    # detector = var_def.DETECT_FILE_ABSOLUTE
    detector = os.path.join(var_def.DETECT_DIR_ABSOLUTE, 'e2detect.add.xml')
    detector_socket = os.path.join(var_def.DETECT_DIR_ABSOLUTE, 'detector_socket.add.xml')
    calibrator = var_def.CALIBRATOR_FILE_ABSOLUTE
    probe = var_def.PROBE_FILE_ABSOLUTE
    #flow_route = os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, 'route.xml')
    #flow_flow = os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, 'flow.xml')

    # the location of the dual_ring_file
    #dual_ring_additional = os.path.join(var_def.TLS_LOGIC_DIR_ABSOLUTE, 'tls.add.xml')

    # The location and name of the vehicle description file:
    veh_description = os.path.join(var_def.VEH_DESCRIPT_DIR_ABSOLUTE, 'vTypeDistributions.add.xml')

    # The location and name of the traffic light output file:
    tl_output_file = os.path.join(var_def.TLS_LOGIC_DIR_ABSOLUTE, 'tls_state_record.add.xml')

    # The location and name of the decal file:
    sim_decal = os.path.join(var_def.DECAL_FILE_DIR_ABSOLUTE, 'decal_settings.xml')

    # the location and name of the random route file (input to calibrator simulation and turnRouter
    random_route = os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, 'routes.xml')
    routeSampler_route = os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, 'route_sampler_sorted.rou.xml')
    calibrator_seed_route = routeSampler_route

    intersection_setup_file = os.path.join(var_def.INTERSECTION_PARAMETERS_ABS, 'intersection_setup_file.xlsx')
    tl_phase_description = os.path.join(var_def.INTERSECTION_PARAMETERS_ABS, 'traffic_light_phasing.xlsx')
    intersection_phasing_file = os.path.join(var_def.INTERSECTION_PARAMETERS_ABS, 'tl_settings.txt')

    # emissions output file
    emissions_output_socket = '127.0.0.1:65433'  # var_def.EMISSIONS_OUTPUT_FILE_ABS
    emissions_probability = '0.05'
    emissions_output_step = '1'
    emissions_output = var_def.EMISSIONS_OUTPUT_FILE_ABS

    # fcd output file
    fcd_output = var_def.FCD_OUTPUT_FILE_ABS
    fcd_probability = '0.1'

    # Trip info file
    trip_info_output = var_def.TRIP_INFO_OUTPUT_FILE_ABS

    # to change the locations/names of the sumo configuration files, change in the SumoConfig class
    route_sampler_config = os.path.join(var_def.SIM_INPUTS_ABSOLUTE, 'hwy69_turnRouter_improved.sumocfg')
    calibrator_config = os.path.join(var_def.SIM_INPUTS_ABSOLUTE, 'hwy69_calibrator_improved.sumocfg')

    # sumo configuration strings. These can be used to run sumo instead on the config xml files. It is written to
    # if get_cmd_line_string() is called
    configuration_string = None
    configuration_list = None

    # the locations of the sumo sim parameters output file. Append each time a simulation is ran.
    parameter_save_file = os.path.join(var_def.SIM_OUTPUT_DATA_DIR, "sim_parameters.txt")

    # simulation output files
    tls_output_file = os.path.join(var_def.TLS_LOGIC_DIR_ABSOLUTE, "tls_state_OUTPUT_.xml")
    detector_output_socket = '127.0.0.1:65432'  # os.path.join(var_def.DETECT_DIR_ABSOLUTE, "_detect_OUTPUT_.xml")
    detector_output_file = os.path.join(var_def.DETECT_DIR_ABSOLUTE, "_detect_OUTPUT_.xml")

    departspeed = 'max'
    vehicle_class = 'vehDist'  # name of the vehicle distribution file

    departspeed_string = f'departSpeed="{departspeed}"'
    vehicle_class_string = f'type="{vehicle_class}"'
    trip_attribute_string = " ".join([departspeed_string, vehicle_class_string])

    @staticmethod
    def get_cmd_line_list(method, emissions=False, sim_step=None, sim_length=None, dual_ring_lights=False,
                          fcd=False, trip_info=False, socket=False):
        """
        This function can be called to get the command line list

        :param socket:
        :param trip_info:
        :param fcd:
        :param method: the simulation "method" aka using calibrators vs. a turnRouter input route file (string)
        :param emissions: a boolean saying whether emissions output files are desired or not. defaults to False
        :param sim_step: the simulation sim_step. defaults to this class's values. should be an float
        :param sim_length: the sim_length. defaults to this class's value
        :param dual_ring_lights: if the lights should be controlled via dual ring controller

        :return: sumo-gui cmd line string
        """

        if socket:
            local_emissions_file = CONFIG.emissions_output_socket
            detector_input = CONFIG.detector_socket
        else:
            local_emissions_file = CONFIG.emissions_output
            detector_input = CONFIG.detector

        specific_string = ""

        # if the sim step and sim_length are not given, then go with the defaults of this class.
        sim_step = CONFIG.sim_step if not sim_step else sim_step
        sim_length = CONFIG.sim_length if not sim_length else sim_length

        # create a string of the desired SUMO cmd line options.
        base_string = ["-n", CONFIG.net_file]
        time_string = ["-e", str(sim_length), "--step-length", str(sim_step)]

        # if the emissions output is desired, then add on the emissions string ###--device.emissions.probability
        # does nothing

        emissions_string = ["--emission-output",  local_emissions_file, "--device.emissions.probability",
                            CONFIG.emissions_probability, "--device.emissions.period", CONFIG.emissions_output_step,
                           "--device.emissions.deterministic", "False"]

        fcd_string = ["--fcd-output", CONFIG.fcd_output, "--device.fcd.probability", CONFIG.fcd_probability,
                      "--fcd-output.acceleration", "--fcd-output.geo"]

        trip_info_string = ["--tripinfo-output", CONFIG.trip_info_output]

        # these additional files are common between all sumo configurations,
        common_additional = ["-a",  CONFIG.veh_description + ", " + detector_input + ", " + CONFIG.tl_output_file]

        if dual_ring_lights:
            common_additional[1] = common_additional[1] + ", " + CONFIG.dual_ring_additional

        if method == "calibrator":
            common_additional[1] = common_additional[1] + ", " + CONFIG.probe + ", " + CONFIG.calibrator
            specific_string = ["-r", CONFIG.calibrator_seed_route] + common_additional

        elif method == "routeSampler":
            specific_string = ["-r", CONFIG.routeSampler_route] + common_additional

        elif method == "flowRouter":
            common_additional[1] = common_additional[1] + ", " + CONFIG.flow_route
            specific_string = ["-r", CONFIG.flow_flow] + common_additional

        elif method == "randomRoutes":
            common_additional[1] = common_additional[1]
            specific_string = ["-r", CONFIG.random_route] + common_additional

        configuration_list = base_string + specific_string + time_string + emissions_string if emissions \
            else base_string + specific_string + time_string

        configuration_list = configuration_list + fcd_string if fcd else configuration_list
        configuration_list = configuration_list + trip_info_string if trip_info else configuration_list

        print(configuration_list)

        CONFIG.configuration_list = configuration_list

        # CONFIG.copy_list =

        return configuration_list

    @staticmethod
    def save_current_status():
        """
        This function can be called to write the simulation parameters to a running text file.
        It is useful for logging what input parameters were used for a given simulation.

        :return: None
        """

        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        real_time_data_string = CONFIG.rw_data_csv + " " + CONFIG.lower_time_bound + " " + CONFIG.upper_time_bound

        # configuration_string = configuration_string if configuration_string \
        #     else configuration_list

        configuration_string = CONFIG.configuration_list

        with open(CONFIG.parameter_save_file, "a") as my_file:
            write_string = \
                            """
            -------------------------------------------------------------------------------------------------
            {time}

            {config_string}

            {real_time_data_string}
            --------------------------------------------------------------------------------------------------
                            """.format(time=dt_string,
                                       config_string=configuration_string,
                                       real_time_data_string=real_time_data_string)

            my_file.write(write_string)
            my_file.flush()


    @staticmethod
    def read_local_config(json_file):

        with open(json_file) as f:
            config_dict = json.load(f)

        input_files = config_dict['input_files']

        if input_files['calibrator'] != "default":
            CONFIG.calibrator = os.path.join(var_def.CALIBRATOR_DIR_ABSOLUTE, input_files['calibrator'])
        if input_files['net_file'] != "default":
            CONFIG.net_file = os.path.join(var_def.NET_FILE_DIR_ABSOLUTE, input_files['net_file'])
        if input_files['detector'] != "default":
            CONFIG.detector = os.path.join(var_def.DETECT_DIR_ABSOLUTE, input_files['detector'])
        if input_files['rw_data_csv'] != "default":
            CONFIG.rw_data_csv = os.path.join(var_def.SQL_DATA_DIR_ABSOLUTE, input_files['rw_data_csv'])
        if input_files['route_file'] != "default":
            CONFIG.calibrator_seed_route = os.path.join(var_def.FLOW_ROUTE_DIR_ABSOLUTE, input_files['route_file'])

        settings = config_dict['settings']

        if settings['sim_step'] != "default":
            CONFIG.sim_step = settings['sim_step']
        if settings['sim_length'] != "default":
            CONFIG.sim_length = settings['sim_length']
        if settings['aggregation_period'] != "default":
            CONFIG.aggregation_period = settings['aggregation_period']
        if settings['intersection_params'] != "default":
            CONFIG.sim_step = settings['intersection_params']  # probably need to specify the path
        if settings['detector_output_freq'] != "default":
            CONFIG.detector_output_freq = settings['detector_output_freq']
        if settings['lower_time_bound'] != "default":
            CONFIG.lower_time_bound = settings['lower_time_bound']
        if settings['upper_time_bound'] != "default":
            CONFIG.upper_time_bound = settings['upper_time_bound']
        if settings['emissions_probability'] != "default":
            CONFIG.emissions_probability = settings['emissions_probability']
        if settings['emissions_output_step'] != "default":
            CONFIG.emissions_output_step = settings['emissions_output_step']




