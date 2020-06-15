import pandas as pd
import datetime
import numpy as np

COLUMNS = ['traffic_light_id', 'Primary', 'Secondary', 'key']
GYR = ['G', 'y', 'r']
PHASE_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]


class RealTimeTrafficLights:
    """
    This class takes in the RW data traffic light status information and turns that into a SUMO 'rGy' string.

    """

    def __init__(self,
                 file_path,
                 ):

        self.data_table = None
        self.tl_ids = list()
        self.key = {}
        self.primary = {}
        self.secondary = {}
        self.string_index = {}

        self.read_xlsx(file_path=file_path)

        self._end_time = None
        self.next_check_time = 0

        self.rw_data = {}
        self.tl_phase_state = {}
        self.tl_phase = {}
        self.tl_phase_string_last = {}
        self._switch_necessary = {}
        self._time_index = {}
        self._primary_ring = {}
        self._primary_ring_last = {}
        self._primary_ring_next = {}
        self._next_phase = {}
        self._ring_cross_color = {}
        self._barrier_cross_next = {}
        self._barrier_cross_allowed = {}
        self._check_index = {}
        self.tl_last_phase = {}
        self.rw_data_indexed = {}
        self._start_time = None

        for ids in self.tl_ids:
            self.tl_phase_state[ids] = ['G', 'G']
            self.tl_phase[ids] = [1, 5]
            self.tl_last_phase[ids] = [1, 5]
            self.tl_phase_string_last[ids] = self.primary[ids]
            self._switch_necessary[ids] = False
            self._primary_ring[ids] = 1
            self._primary_ring_last[ids] = 0
            self._primary_ring_next[ids] = 0
            self._next_phase[ids] = [1, 5]
            self._ring_cross_color[ids] = 'y'
            self._barrier_cross_next[ids] = False
            self._time_index[ids] = 0
            self._check_index[ids] = 0
            self._barrier_cross_allowed[ids] = False

    def read_xlsx(self, file_path):

        self.data_table = pd.read_excel(file_path)
        self.data_table[COLUMNS[0]] = self.data_table[COLUMNS[0]].astype(str)

        self.tl_ids = self.set_traffic_light_ids()
        self.key = self.set_tllogic_string_index()
        self.primary = self.set_primary_string()
        self.secondary = self.set_secondary_string()
        self.string_index = self._pre_index_tl_string()

    def set_traffic_light_ids(self):
        return self.data_table[COLUMNS[0]].values.tolist()

    def set_primary_string(self):
        dictionary = {}
        for tl_id in self.tl_ids:
            dictionary[tl_id] = self.data_table[COLUMNS[1]].loc[(self.data_table[COLUMNS[0]] == tl_id)].values.tolist()[
                0]
        return dictionary

    def set_secondary_string(self):
        dictionary = {}
        for tl_id in self.tl_ids:
            dictionary[tl_id] = self.data_table[COLUMNS[2]].loc[(self.data_table[COLUMNS[0]] == tl_id)].values.tolist()[
                0]
        return dictionary

    def set_tllogic_string_index(self):

        dictionary = {}

        for tl_id in self.tl_ids:
            local_list = \
                self.data_table[COLUMNS[3]].loc[(self.data_table[COLUMNS[0]] == tl_id)].values.tolist()[0].split(',')
            dictionary[tl_id] = [int(i) for i in local_list]

        return dictionary

    def read_in_rw_data(self, dictionary, start_time=0, end_time=1000):

        """
        This function reads in the traffic light event dictionary from the RWTrafficData class.

        It transforms that format into {tl_id: np.array([time, phase, state])} where state is 0 if G, 1 if Y, 2 if R

        traffic_light_manager class takes care of the formatting for the start_time and end_time

        :param dictionary: from RWTrafficData
        :param start_time:
        :param step:
        :param end_time:
        :return:
        """

        self.rw_data = dictionary
        self._end_time = end_time
        self._start_time = start_time
        self.rw_data_indexed = {key: None for key in self.rw_data}

        # switch pandas dataframe to numpy array. It is quicker to index np arrays.
        # It may be possible to predetermine simulation timesteps where the lights will be written to.
        for item in self.rw_data.items():

            dict_list = []

            for i in range(3):
                local_dict = pd.DataFrame(item[1][i])[self._start_time:self._end_time]
                local_dict['state'] = int(i)
                dict_list.append(local_dict)

            # write to the concatenated dictionary pd.DataFrame(item[1][i])y and sort
            concat_dict = pd.concat(dict_list).sort_index()

            # convert the dictionary to a numpy array for increased indexing speed.
            self.rw_data_indexed[item[0]] = np.array([concat_dict.index, concat_dict.values[:, 0],
                                                      concat_dict.values[:, 1]]).T

            self.tl_last_phase[item[0]] = self.rw_data_indexed[item[0]][0, 1]

            # An override for it the first phase is only of length 1. The length must be = to 2 for the algorithm to
            # work.
            if len(self.tl_last_phase[item[0]]) != 2:
                local = [""] * 2
                if self.tl_last_phase[item[0]][0] < 5:
                    local[0] = self.tl_last_phase[item[0]][0]
                else:
                    local[1] = self.tl_last_phase[item[0]][0]
                self.tl_last_phase[item[0]] = local

    def _set_switch_necessary(self, sim_time, step):

        """
        :param sim_time: the rw time
        :param step: the step length
        :return: self
        """

        # get the next time to determine the step interval
        next_time = sim_time + datetime.timedelta(seconds=step)

        # set the next check time to the simulation end time
        self.next_check_time = self._end_time

        # loop through the traffic lights
        for tl_id in self.tl_ids:

            # switch necessary is the flag to determine if a light state should be written
            self._switch_necessary[tl_id] = False

            # get the light change and state corresponding to the time indexer. A time indexer is used to speed up
            # the queries as opposed to indexing by time comparision
            time, data, state = self.rw_data_indexed[tl_id][self._time_index[tl_id], :]

            # if the light change time is less than or = the next step time, then action
            if time <= next_time:

                # This commented out if statement is useful for debugging if there is unusual behavior to be checked
                # if time >= datetime.datetime.strptime('02/05/2020 07:05:13.500', '%m/%d/%Y %H:%M:%S.%f'):
                #     x = 0
                #
                if time >= datetime.datetime.strptime('02/05/2020 07:05:11.000', '%m/%d/%Y %H:%M:%S.%f'):
                    x = 0

                for phase in data:
                    # write the phase and the state
                    if phase > 4:
                        self.tl_phase[tl_id][1] = phase
                        self.tl_phase_state[tl_id][1] = GYR[state]
                    else:
                        self.tl_phase[tl_id][0] = phase
                        self.tl_phase_state[tl_id][0] = GYR[state]

                self._switch_necessary[tl_id] = True

                self._time_index[tl_id] += 1

                # make sure that the index doesnt grow greater than the length of the index.
                self._time_index[tl_id] = min(self._time_index[tl_id],
                                              len(self.rw_data_indexed[tl_id][:, 0]) - 1)

            # The try/except statement deals with the end of the RW data
            try:
                next_green_index = np.where(self.rw_data_indexed[tl_id][self._time_index[tl_id]:,
                                            2] == 0)[0][0] + self._time_index[tl_id]
                self._next_phase[tl_id] = self.rw_data_indexed[tl_id][next_green_index, 1]
                # self._next_phase[tl_id] = self.rw_data_indexed[tl_id][self._time_index[tl_id], 1]

            except IndexError:
                self._next_phase[tl_id] = ["", ""]

            # get the next time
            try:
                self.next_check_time = min(self.next_check_time,
                                           self.rw_data_indexed[tl_id][self._time_index[tl_id], 0]
                                           )
            except IndexError:
                print("Next Check Time doesn't exist")

    def update_light_states(self, sim_time, step):
        """
        This is the main function of the RealTimeTrafficLights class.

        It checks if switch is necessary. If so, then it checks if there is a barrier cross event (_primary_or_side_street_correct)

        After that check is made it will generate a light string and return that string

        :param sim_time: the current simulation time (in rw format, with date and time). This is used to check if a light change should be made
        :param step: the simulation step size. (this probably can be made static in an intialization function but **shrug**
        :return: phase_dict: {tl_id: {'light_string': str(),
                                      'phase_name': str(),
                                      'phase_state': [str(), str()]}
                              }
                next_check_time: the rw_time in which a change happens
        """

        self._set_switch_necessary(sim_time, step)

        phase_dict = {tl_id: {} for tl_id in self.tl_ids if self._switch_necessary[tl_id]}

        for tl_id in phase_dict:
            self._primary_or_side_street_correct(tl_id)
            phase_dict[tl_id]['light_string'] = self._get_light_string(tl_id)
            phase_dict[tl_id]['phase_name'] = str(self.tl_phase[tl_id][0]) + "-" + str(self.tl_phase[tl_id][1])
            phase_dict[tl_id]['phase_state'] = self.tl_phase_state[tl_id]
            self.tl_phase_string_last[tl_id] = phase_dict[tl_id]['light_string']
            self.tl_last_phase[tl_id] = self.tl_phase[tl_id].copy()
            self._primary_ring_last[tl_id] = self._primary_ring[tl_id]

        return phase_dict, self.next_check_time

    def _get_light_string(self, tl_id):

        # phase_string = self.tl_phase_string_last[tl_id]

        # if there is a barrier cross event, then find all of the traffic light states 's or y' that need to be replaces
        if self._barrier_cross_allowed[tl_id]:

            index = [j for j, letter in enumerate(self.tl_phase_string_last[tl_id]) if
                     ((self._ring_cross_color[tl_id] == 'y') and (letter == 'G' or letter == 'g')) or
                     ((self._ring_cross_color[tl_id] == 'r') and (letter == 'y' or letter == 's'))]

            phase_string = self.primary[tl_id] if self._primary_ring_next[tl_id] else self.secondary[tl_id]

            if self._ring_cross_color[tl_id] != 'G':
                yield_list = [j for j, letter in enumerate(phase_string) if letter == 'g']
                if len(yield_list) > 0:
                    yield_phases = list(set([self.key[tl_id][j] for j in yield_list]))
                    linked_phase = [yield_phase for yield_phase in yield_phases
                                    if self._barrier_cross_next[tl_id]]
                    if len(linked_phase) > 0:
                        for link_phase in linked_phase:
                            index += self.string_index[tl_id][link_phase]

            for string_index in index:
                phase_string = phase_string[:string_index] + self._ring_cross_color[tl_id] + \
                               phase_string[string_index + 1:]

            return phase_string

        else:
            # added logic to deal with the yielding left turns
            phase_string = self.primary[tl_id] if self._primary_ring[tl_id] else self.secondary[tl_id]

            for i, phase in enumerate(self.tl_phase[tl_id]):

                if phase != "":

                    index = self.string_index[tl_id][phase].copy()

                    if self.tl_phase_state[tl_id][i] != 'G':

                        yield_list = [j for j, letter in enumerate(phase_string) if letter == 'g']

                        if len(yield_list) > 0:

                            yield_phases = list(set([self.key[tl_id][j] for j in yield_list]))
                            # sum_total = 7 if self._primary_ring[tl_id] else 11
                            # linked_phase = [yield_phase for yield_phase in yield_phases if
                            #                 (yield_phase + phase == sum_total) or self._barrier_cross_next[tl_id]]
                            linked_phase = [yield_phase for yield_phase in yield_phases
                                            if self._barrier_cross_next[tl_id]]

                            if len(linked_phase) > 0:
                                for link_phase in linked_phase:
                                    index += self.string_index[tl_id][link_phase]

                    for string_index in index:
                        phase_string = phase_string[:string_index] + self.tl_phase_state[tl_id][i] + \
                                       phase_string[string_index + 1:]

            return phase_string

    def _primary_or_side_street_correct(self, tl_id):

        # create the empty local variables
        primary = ["", ""]
        reshuffled = ["", ""]
        reshuffled_state = ["", ""]
        future_phase_primary = ["", ""]

        # set the barrier cross flag to false
        self._barrier_cross_next[tl_id] = False
        self._barrier_cross_allowed[tl_id] = False

        # this for loop determines if the phases are serving primary or secondary streets
        for j, phase in enumerate(self.tl_phase[tl_id]):
            phase_state = self.tl_phase_state[tl_id][j]
            if phase != "":
                if phase > 4:
                    reshuffled[1] = phase
                    reshuffled_state[1] = phase_state
                    if phase > 6:
                        primary[1] = False
                    else:
                        primary[1] = True
                else:
                    reshuffled[0] = phase
                    reshuffled_state[0] = phase_state
                    if phase > 2:
                        primary[0] = False
                    else:
                        primary[0] = True

        # this for loop replaces an empty phase state with the other phase state. For example, [4,""] becomes [4,4]
        for i, val in enumerate(primary):
            if primary[i] == "":
                primary[i] = primary[i - 1]

        # test if the barrier has been crossed correctly. This logic is needed because certain lights will go from
        # [2, 6] to [3]. This is initially interpreted as [3,6] which is not possible. It should be corrected from [3,
        # 6] -> [3]
        if not primary[0] is primary[1]:
            i = 0
            flag = False
            while (i < 2) & (flag is False):
                # ring cross only occurs on a green phase
                if reshuffled_state[i] == "G":
                    flag = True
                i += 1

            if flag:
                replace_id = [i for i, number in enumerate(reshuffled) if number == self.tl_last_phase[tl_id][i]][0]
                reshuffled[replace_id] = ""
                reshuffled_state[replace_id] = ""

        not_green = False
        for color in reshuffled_state:
            if (color != 'G') & (color != ""):
                not_green = True

        # if any of the phases are not green, then we need to look at the future state to determine what if a
        # barrier cross is coming. If so, not only do (for example) [2,6] need to be set to yellow, but so do [1,5]
        # yielding green.

        if not_green:

            #future_phase_primary = ["", ""]
            reshuffled_future = ["", ""]

            for j, phase in enumerate(self._next_phase[tl_id]):
                if phase != "":
                    if phase > 4:
                        reshuffled_future[1] = phase
                        if phase > 6:
                            future_phase_primary[1] = False
                        else:
                            future_phase_primary[1] = True
                    else:
                        reshuffled_future[0] = phase
                        if phase > 2:
                            future_phase_primary[0] = False
                        else:
                            future_phase_primary[0] = True

            if len([i for i, phase in enumerate(future_phase_primary) if (primary[i] != phase) and (phase != "")]) > 0:
                # ring is crossed on the next green:
                self._barrier_cross_next[tl_id] = True
                self._ring_cross_color[tl_id] = [letter for i, letter in
                                                 enumerate(reshuffled_state) if letter != ""][0]

            # Check if a barrier cross is allowed. aka the phases are red
            if self._barrier_cross_next[tl_id]:
                if (reshuffled_state[0] == 'r') and (reshuffled_state[1] == 'r'):
                    self._barrier_cross_allowed[tl_id] = True
                elif (reshuffled[0] == "") and (reshuffled_state[1] == 'r'):
                    self._barrier_cross_allowed[tl_id] = True
                elif (reshuffled[1] == "") and (reshuffled_state[0] == 'r'):
                    self._barrier_cross_allowed[tl_id] = True

        for j, future_primary in enumerate(future_phase_primary):
            if future_primary == "":
                future_phase_primary[j] = future_phase_primary[j-1]

        self.tl_phase[tl_id] = reshuffled
        self.tl_phase_state[tl_id] = reshuffled_state
        self._primary_ring[tl_id] = primary[0] * primary[1]
        try:
            self._primary_ring_next[tl_id] = future_phase_primary[0] * future_phase_primary[1]
        except TypeError:
            self._primary_ring_next[tl_id] = self._primary_ring[tl_id]

    def _pre_index_tl_string(self):
        """

        :return:
        """

        indices_set = {phase: None for phase in PHASE_LIST}
        indices_dict = {tl_id: indices_set for tl_id in self.tl_ids}

        for tl_id in indices_dict.keys():
            indices = {}
            for phase in indices_dict[tl_id].keys():
                indices.update(
                    {phase: [tl_string_index for tl_string_index, key in enumerate(self.key[tl_id]) if key == phase]})
            indices_dict.update({tl_id: indices})

        return indices_dict

    # def _get_yielding_indexes(self):
