from functions.SQL.rw_traffic_data import RWTrafficData
from functions.traffic_lights.real_time_traffic_light import RealTimeTrafficLights
import datetime
import pandas as pd


class TrafficLightManager:

    def __init__(self,
                 end_time,
                 traffic_light_phasing,
                 rw_start_time,
                 rw_csv_data,
                 traffic_light_ids
                 ):

        if isinstance(rw_start_time, str):
            self.rw_start_time = datetime.datetime.strptime(rw_start_time, '%m/%d/%Y %H:%M:%S.%f')
        else:
            self.rw_start_time = rw_start_time

        end_time_dt = self.convert_to_datetime(end_time)

        self.traffic_data = RWTrafficData(rw_csv_data)

        self.light_event_dict = self.traffic_data.active_phase_events.get_light_events()

        self.traffic_light = RealTimeTrafficLights(traffic_light_phasing,
                                                   )

        self.traffic_light.read_in_rw_data(dictionary=self.light_event_dict,
                                           start_time=self.rw_start_time,
                                           end_time=end_time_dt)

    def get_light_string(self, sim_time, step_time):

        time = self.convert_to_datetime(sim_time)

        return self.traffic_light.update_light_states(sim_time=time, step=step_time)

    def convert_to_datetime(self, sim_time):

        return self.rw_start_time + datetime.timedelta(seconds=sim_time)

    def convert_from_datetime(self, date_time=None):

        if date_time is None:
            date_time = self.rw_start_time

        # Have to use microseconds because seconds rounds to the nearest second.
        return pd.Timedelta(date_time - self.rw_start_time).total_seconds()

