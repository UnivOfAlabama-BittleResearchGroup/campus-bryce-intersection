from distutils import util
import pandas as pd
import numpy as np
import ast

def _sort_desired(data):
    """
    this function is called iteratively down the SQL data, changing the enumerated event parameters into integers and
    sorting from small to large
    :param data: a row of pandas data
    :return: the formatted row
    """
    inted = [int(phase) for phase in data['EventParam']]
    state = [data['state']] * 2
    return [(y, x) for y, x in sorted(zip(inted, state))]


def _value_error_handler(tuple_obj, default):
    """
    This function handles trying to unpack an empty tuple
    :param tuple_obj: tuple to unpack
    :param default: the empty tuple value
    :return:
    """
    try:
        x, y = tuple_obj
        return x, y
    except ValueError:
        return default


class Observable(object):
    """From: https://stackoverflow.com/questions/44499490/alternate-ways-to-implement-observer-pattern-in-python
       This class is what allows the linked lights to communicate with one another. When an "observed light" aka phase 6
       changes color, say from r -> g, it notifies its observers.
       Its observer would be phase 1, and that phase will then do it's decision logic based on major/minor linked
       phases and the state it is already in
    """
    def __init__(self):
        self.observers = []
        self.deciders = []

    def register(self, fn):
        """
        register(fn) appends the observer function list
        :param fn: a function
        :return: None
        """
        self.observers.append(fn)

    def register_decision_logic(self, fn):
        """
        registers a decision logic function
        :param fn: a function
        :return: None
        """
        self.deciders.append(fn)

    def notify_observers(self, *args, **kwargs):
        """
        This function is called from the point of view of an observed light head and notifies the observers,
        and then calls their decision logic
        :param args:
        :param kwargs:
        :return:
        """
        for notify, decide in zip(self.observers, self.deciders):
            notify(*args, **kwargs)
            decide(*args, **kwargs)


class LightHead(Observable):

    light_states = ['g', 'y', 'r']
    allowed_move = {'g': ['y', 'g', 'yield'],
                    'y': ['r', 'y'],
                    'r': ['g', 'y', 'yield'],
                    'yield': ['g', 'y']}

    def __init__(self, phase_name, green_string, yellow_string, red_string):
        """
        This class represents a "light head", that is a string of letters that move together.
        i.e. phase 6 on 63069006 is 'GGGG' or 'srrr' (s meaning right on red)
        :param phase_name: the name of the phase ( 6 -> 'six')
        :param green_string: the string of letter representing a green
        :param yellow_string: ^^
        :param red_string: ^^
        """
        super().__init__()
        self.phase_name = phase_name
        self.color = LightHead.light_states[-1]
        self._last_changed_time = 0
        self._string = {'g': green_string,
                        'y': yellow_string,
                        'r': red_string}
        self._paired_phase_actions = {}
        self._paired_priority = {}

    def link_yield_observer(self, priority, yield_string, paired_phase):
        """
        If a phase needs to observe another (1 needs to know 2 & 6 to decide to yield or not) this function is called
        to link the phase and the observed phase
        :param priority: the priority ('main' or 'secondary')
        :param yield_string: the string for yielding i.e. 'gggg'
        :param paired_phase: the paired phase (not the name but the actual object)
        :return: None
        """
        if yield_string:
            self._string['yield'] = yield_string
            self._paired_priority[priority] = paired_phase.phase_name
            self._paired_phase_actions[paired_phase.phase_name] = ()
            paired_phase.register(self.yield_observer)
            paired_phase.register_decision_logic(self.process_observations)

    def transition(self, desired, time):
        """
        transition the light if it is an allowed move. See allowed_move
        :param desired: the desired color
        :param time: the simulation time
        :return: Boolean representing the success of the transition
        """
        if desired in LightHead.allowed_move[self.color]:
            self.color = desired
            self._last_changed_time = time
            self.update_observers()
            return True
        return False

    def update_observers(self):
        """
        update the observers from the point of view of the observed. i.e. if 6 is observed by 1, then when 6 changes its
        state, see transition(), it will notify 1 of the change and 1 may change its state based on logic in
        process_observation()
        :return:
        """
        if self.observers:
            self.notify_observers(self.phase_name, self.color, self._last_changed_time)

    def force_transition(self, desired, time):
        """
        force a transition without checking whether it is okay
        :param desired: the desired color
        :param time: the simulation time
        :return:
        """
        self.color = desired
        self._last_changed_time = time

    def get_string(self):
        """
        Get the light string for the specified color
        :return:
        """
        return self._string[self.color]

    def yield_observer(self, phase_name, paired_phase_color, time):
        """
        yield_observer() is triggered by phase 1, for example, when phase 6 calls update_observers(). This function
        stores information about the paired phase' actions.
        For 1 to make a decision whether to yield or not, it needs to have the states and update times of both 6 and 2
        :param phase_name: name of the phase that I am storing
        :param paired_phase_color: the color of the phase that I am storing
        :param time: the time of the change
        :return:
        """
        self._paired_phase_actions[phase_name] = (paired_phase_color, time)

    def process_observations(self, *args, **kwargs):
        """
        This is the function called by 1 to decide what phase to go to when 2 and 6 are updated.
        This function is necessary because the SQL database doesn't report on yield actions
        :param args: same as yield_observer() inputs
        :param kwargs:
        :return:
        """
        if len(self._paired_priority) < 2:
            paired_name = self._paired_priority['main']
            paired_light_color, time = self._paired_phase_actions[paired_name]
            if time > self._last_changed_time:
                self._last_changed_time = time
                if (paired_light_color == 'g') and (self.color != 'g'):
                    self.color = 'yield'
                elif self.color != 'g':
                    # Only when I am not green do I do what the master light is doing
                    self.color = paired_light_color
        else:
            main_name = self._paired_priority['main']
            secondary_name = self._paired_priority['secondary']
            main_light_color, main_time = _value_error_handler(self._paired_phase_actions[main_name], default=('g', 1e6))
            secondary_light_color, secondary_time = _value_error_handler(self._paired_phase_actions[secondary_name],
                                                                         default=('g', 1e6))
            most_recent_time = max([main_time, secondary_time])
            if self._last_changed_time <= most_recent_time:
                self._last_changed_time = args[2]  # this is the actual time
                if secondary_light_color == 'g' == main_light_color:
                    self.color = 'yield'
                elif main_light_color != 'g':
                    self.color = main_light_color


class DualRingTL:
    name_map = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}

    def __init__(self, name, phase_dict, string_order):
        """
        Represents one traffic light
        :param name:
        :param phase_dict: should be a dict of phase numbers {1: {lane_num: 3, right_on_red: No, yield_for: 6},
                            2: {yield_for: None}, 3: {yield_for: 8}...}
        :param string_order: a list of the order phase strings should be joined in
        """
        self.name = name
        self.light_heads = self._compose_light_heads(phase_dict)
        self._active_1_4 = (2, 'g')  # initialize as something
        self._active_5_8 = (6, 'g')
        self.string_order = string_order

    def change_light(self, desired_action, sim_time):
        """
        called by the HistoricalLightManager
        :param desired_action: the desired action passed by the HistoricalLightManager. Of form [(2, 'g), (6, 'y')]
        :param sim_time: the time of the simulation
        :return: the light string
        """
        barrier_cross = self._barrier_cross_desired(desired_action)
        if barrier_cross:
            if self._ok_to_cross_barrier():
                self._implement_desired(desired_action, sim_time)
            else:
                # this happens initially when SQL control comes in and overtakes the SUMO control
                print("Barrier Cross Desired but not allowed. Doing it anyway")
                # need to set all lights to red and then implement the desired action
                self._force_all_red(sim_time)
                self._implement_desired(desired_action, sim_time)
        else:
            self._implement_desired(desired_action, sim_time)
        return self._get_light_string()

    def forcibly_change_light(self, desired_action, sim_time):
        for phase, color in desired_action:
            self.light_heads[phase].force_transition(color, sim_time)
        return self._get_light_string()


    def _force_all_red(self, time):
        """
        force all the lights to red

        :return: None
        """
        for head in self._iterate_light_heads():
            head.force_transition('r', time)

    def _get_light_string(self):
        """
        join the individual light strings together. iterate through the light heads in the order specified
        by self.string_order.
        :return:
        """
        light_string = ""
        for index in self.string_order:
            light_string = "".join([light_string, self.light_heads[index].get_string()])
        return light_string

    def _iterate_light_heads(self):
        """
        create an iterator to loop through the light heads
        :return: yielding a light head
        """
        for head in self.light_heads.values():
            yield head

    def _implement_desired(self, desired_action, sim_time):
        """
        take the desired action from change_light() and try to implement it.
        :param desired_action: from HistoricalLightManager
        :param sim_time: ^^
        :return:
        """
        for phase, color in desired_action:
            success = self.light_heads[phase].transition(color, sim_time)
            if not success:
                print("Transition not allowed. Overriding..", phase, color)
                self.light_heads[phase].force_transition(color, sim_time)
            if (phase < 5) and (color == 'g'):
                self._active_1_4 = (phase, color)
            elif (phase >= 5) and (color == 'g'):
                self._active_5_8 = (phase, color)

    def _ok_to_cross_barrier(self):
        """
        check if it is okay for the light to cross it's barrier
        :return: ok or not (Boolean)
        """
        for light in self._iterate_light_heads():
            if light.color != 'r':
                # light.transition('r', )
                return False
        return True

    def _barrier_cross_desired(self, desired_actions):
        """
        see if the intended move is a barrier cross event
        :param desired_actions: from HistoricalLightManager
        :return: Boolean
        """
        # desired action is already sorted small to big
        top_side_actual = self._active_1_4[0] < 3
        bottom_side_actual = self._active_5_8[0] < 7
        for i, phase_color in enumerate(desired_actions):
            phase = phase_color[0]
            color = phase_color[1]
            if color != 'g':
                return False
            if phase < 5:
                top_side_desired = phase < 3
                if top_side_desired != top_side_actual:
                    return True
            else:
                bottom_side_desired = phase < 7
                if bottom_side_desired != bottom_side_actual:
                    return True

    def _compose_light_heads(self, phase_dict):
        """
        This is called once. The phase dict from the settings file is passed and the light heads are created and
        associated to each DualRingTL
        :param phase_dict: comes from tl_settings.txt
        :return: the light heads in dict() form
        """
        self._phases = [key for key in sorted(phase_dict.keys())]
        yields_to_loop = []
        light_heads = {}
        for phase in self._phases:
            phase_info = phase_dict[phase]
            lanes = phase_info['lane_num']
            if phase_info['yield_for']:
                yields_to_loop.append(phase)
            red_string = 'r' * lanes if not bool(
                util.strtobool(phase_info['right_on_red'])) else 's' + 'r' * (lanes - 1)
            light_heads[phase] = LightHead(phase_name=DualRingTL.name_map[phase],
                                           green_string='G' * lanes,
                                           yellow_string='y' * lanes,
                                           red_string=red_string,
                                           )
        for yield_phase in yields_to_loop:
            phase_info = phase_dict[yield_phase]
            lanes = phase_info['lane_num']
            for paired_info in phase_info['yield_for'].items():
                paired_light = light_heads[paired_info[1]]
                light_heads[yield_phase].link_yield_observer(yield_string='g' * lanes, priority=paired_info[0],
                                                             paired_phase=paired_light)
        return light_heads


class HistoricalLightManager:
    state_map = {1: 'g', 2: 'y', 3: 'r'}

    def __init__(self, step):
        """
        Translates the SQL database into an action for the SUMO traffic lights
        :param step: the step size of the simulation
        """
        self._end_time = 0
        self._start_time = 0
        self.rw_data_indexed = {}
        self._step = step
        self.traffic_lights = {}
        self.traffic_light_names = []
        self._array_index = {}

    def add_traffic_light(self, name, phase_dict, string_order):
        """
        Called iteratively from a level higher. US69 for example has 4 traffic lights so this function is called 4 times
        :param name: the name of the light (string)
        :param phase_dict: the phase for each light
        :param string_order: the order of the phases as they come in the string
        :return: None
        """
        self.traffic_lights[name] = DualRingTL(name, phase_dict, string_order)
        self.traffic_light_names.append(name)
        self._array_index[name] = 0

    def read_in_rw_data(self, dictionary, start_time, end_time):
        """
        This function reads in and stores the SQL database data, tranforming it into a simpler-to-process format
        :param dictionary: the SQL data in format {'tl1': pd.DataFrame(), 'tl2': ..}
        :param start_time: the start time of the simulation in datetime
        :param end_time: the end time of simulation in datetime
        :return:
        """
        self._end_time = end_time
        self._start_time = start_time
        self.rw_data_indexed = {key: None for key in dictionary}
        # switch pandas dataframe to numpy array. It is quicker to index np arrays.
        # It may be possible to predetermine simulation timesteps where the lights will be written to.
        for item in dictionary.items():
            dict_list = []
            for i in range(3):
                local_dict = pd.DataFrame(item[1][i])[self._start_time:self._end_time]
                local_dict['state'] = HistoricalLightManager.state_map[i + 1]
                dict_list.append(local_dict)
            # write to the concatenated dictionary pd.DataFrame(item[1][i])y and sort
            concat_dict = pd.concat(dict_list).sort_index()
            # convert the dictionary to a numpy array for increased indexing speed.
            reformated_phase_color = concat_dict.apply(_sort_desired, axis=1)
            # change the datetimeindex to just datetime
            concat_dict['dt'] = concat_dict.index.to_pydatetime()
            # find the timedelta
            timedelta = concat_dict['dt'] - start_time
            # convert to seconds since simulation start
            timedelta_total = timedelta.dt.days * 24 * 60 * 60 + timedelta.dt.seconds + timedelta.dt.microseconds / 1e6
            self.rw_data_indexed[item[0]] = np.array([timedelta_total.values, reformated_phase_color.values]).T

    def compute(self, sim_time):
        """
        This function is called in the Traci runner script. it takes in the simulation time and indexes the SQL data
        to find the correspondng action. It returns the action to be taken in form of a string and the next simulation
        time that correlates with an action
        :param sim_time: time
        :return: light_strings = {'tl1': None, 'tl2': 'rrrGGGGg'...}, next_time
        """
        next_time = 1e9
        light_strings = {}
        for tl_id in self.traffic_light_names:
            light_strings[tl_id] = None
            array_index = self._array_index[tl_id]
            try:
                time, desired_change = self.rw_data_indexed[tl_id][array_index, :]
                if sim_time + self._step > time:
                    # take action
                    light_strings[tl_id] = self.traffic_lights[tl_id].change_light(desired_change, sim_time)
                    array_index += 1
                    next_time = self.rw_data_indexed[tl_id][array_index, 0] if \
                        self.rw_data_indexed[tl_id][array_index, 0] < next_time else next_time
                    self._array_index[tl_id] = array_index
                else:
                    next_time = time if time < next_time else next_time
            except IndexError:
                #  This catches the indexing error that occurs after the SQL data ends. Try Except faster than if
                #  else I think. No action is needed so move on
                continue
        return light_strings, next_time


class SILLightManager:

    state_map = {1: 'g', 2: 'y', 3: 'r'}

    def __init__(self, tl_settings_file):
        """
        Translates the SQL database into an action for the SUMO traffic lights
        :param step: the step size of the simulation
        """
        self.traffic_lights = {}
        self.traffic_light_names = []
        self._array_index = {}

        for tl_id, settings, phase_order in self._read_process_tl_settings(tl_settings_file):
            self.add_traffic_light(name=tl_id, phase_dict=settings, string_order=phase_order)

    def add_traffic_light(self, name, phase_dict, string_order):
        """
        Called iteratively from a level higher. US69 for example has 4 traffic lights so this function is called 4 times
        :param name: the name of the light (string)
        :param phase_dict: the phase for each light
        :param string_order: the order of the phases as they come in the string
        :return: None
        """
        self.traffic_lights[name] = DualRingTL(name, phase_dict, string_order)
        self.traffic_light_names.append(name)
        self._array_index[name] = 0

    def get_light_strings(self, state_dict, sim_time):
        light_strings = {}
        for item in state_dict.items():
            if item[1]:
                # self.traffic_lights[item[0]]._force_all_red(sim_time)
                light_strings[item[0]] = self.traffic_lights[item[0]].forcibly_change_light(item[1], sim_time)
        return light_strings

    @staticmethod
    def _read_process_tl_settings(file_name):
        """
        reads in the tl_settings.txt file and converts it to a dictionary to initialize tne tl_fsm classes

        :param file_name: the file path that points to the tl_settings.txt
        :return: an iterator of the light settings
        """
        # reading the data from the file
        with open(file_name) as f:
            data = f.read()
        d = ast.literal_eval(data)
        for item in d.items():
            yield item[0], item[1]['individual_settings'], item[1]['phase_order']
