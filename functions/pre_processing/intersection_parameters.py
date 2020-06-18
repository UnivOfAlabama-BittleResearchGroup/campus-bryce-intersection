import pandas as pd
import numpy as np

header = ["Human_Identifier", "ID", "tl", "Edge", "Lane", "Sumo_Detector", "RW_Detector", "Detector_Distance",
          "Sumo_Detector_2", "RW_Detector_2", "Detector_2_Distance"]


class IntersectionParameters:
    """
    IntersectionParameters is for processing the intersection setup file.

    There are a number of functions that basically perform the same function. This file could be reworked. It is used
    by most of the higher level scripts though, so there will be a fair amount of effort involved.

    """
    def __init__(self):
        self.df = pd.DataFrame()
        self.detector_array = np.array([])

    def import_file(self, file_path):
        self.df = pd.read_excel(file_path, )

        # self.df['count_of_RW_detect'] =

    def get_match(self, traffic_light_id, detect):
        try:
            return self.df.loc[
                (self.df["ID"] == traffic_light_id) & (self.df["Sumo_Detector"] == detect)].RW_Detector.value
        except TypeError:
            return 0.

    def get_unique_tl(self):
        return map(str, self.df["tl"].unique())

    def get_rw_index_by_light(self, traffic_light_id, main=True, dict=False):
        local_df = self.df.loc[(self.df["ID"] == traffic_light_id)]

        RW_DETECT = 'RW_Detector' if main else "RW_Detector_2"
        SUMO_DETECT = "Sumo_Detector" if main else "Sumo_Detector_2"

        local_df.sort_values(by=[RW_DETECT], ascending=False, inplace=True)
        local_df = local_df[local_df[RW_DETECT].notna()]

        if dict:
            return {local_df.loc[idx, SUMO_DETECT]: local_df.loc[idx, RW_DETECT] for idx in local_df.index}
        else:
            return [list(local_df[SUMO_DETECT]), list(local_df[RW_DETECT])]

    def get_detectors_per_light(self, traffic_light_id):
        local_df = self.df.loc[(self.df["ID"] == int(traffic_light_id))]
        count_df = local_df.groupby('RW_Detector').size()
        count = [count_df[detect] for detect in local_df.RW_Detector]
        self.detector_array = np.vstack([local_df.Sumo_Detector, local_df.RW_Detector, count])

    def get_matching_info(self, detector):
        try:
            
            last = detector[-1]

            if last == '2':
                # Find the matching RW Detector ID
                rw_id = self.get_match_from_column("RW_Detector_2", 'Sumo_Detector_2', detector)
                tl_id = self.get_match_from_column("tl", "Sumo_Detector_2", detector)
                # Use the RW Detector ID & TL_ID to find all the sumo detectors with that RW ID
                detect_list = self.df.loc[(self.df["RW_Detector_2"] == rw_id) &
                                          (self.df["tl"] == tl_id)]['Sumo_Detector_2'].values
            else:
                # Find the matching RW Detector ID
                rw_id = self.get_match_from_column("RW_Detector", 'Sumo_Detector', detector)
                tl_id = self.get_match_from_column("tl", "Sumo_Detector", detector)
                # Use the RW Detector ID & TL_ID to find all the sumo detectors with that RW ID
                detect_list = self.df.loc[(self.df["RW_Detector"] == rw_id) &
                                          (self.df["tl"] == tl_id)]['Sumo_Detector'].values

            return {'rw_id': rw_id, 'detect_list': detect_list}

        except IndexError:
            return 'Detector does not Exist in the Equivalency File'

    def get_unique_sumo_detectors(self):
        return self.df.Sumo_Detector.unique()

    def get_unique_edges(self):
        return self.df.Edge.unique()

    def get_unique_lanes(self):
        return self.df.Lane.unique()

    def get_match_from_column(self, desired_column, search_column, match_value):
        return self.df.loc[self.df[search_column] == match_value][desired_column].values[0]

    def get_count_of_df(self, search_column, search_value, count_column, match_column, match_value):
        local_df = self.df.loc[self.df[search_column] == search_value]
        value_counts = local_df[count_column].value_counts()
        return value_counts[self.df.loc[self.df[match_column] == match_value][count_column]].values[0]

    def get_secondary_detect(self, lane):
        return [self.df.loc[self.df['Lane'] == lane].Sumo_Detector_2.values[0] if
                self.df.loc[self.df['Lane'] == lane].RW_Detector_2.values[0] > 0 else []][0]

    def get_tl_id_from_sumo_detect(self, detector):
        # check to see if detector is secondary detector (name will end with '2'
        try:
            last = detector[-1]
            if last == '2':
                return str(self.df.loc[self.df['Sumo_Detector_2'] == detector].tl.values[0])
            return str(self.df.loc[self.df['Sumo_Detector'] == detector].tl.values[0])
        except IndexError:
            return 'Detector does not Exist in the Equivalency File'

    def write_df(self, df):
        self.df = df

    def write_to_excel(self, excel_path):
        self.df.to_excel(excel_path, index=False)

    def _set_slicer_locations(self, methods=None, values=None, and_or=None):
        detect_slice = [self.df.RW_Detector.notna(), self.df.RW_Detector_2.notna()]
        if methods:
            for method in iter(methods):
                local = list(self.df[method] == values[method][0])
                for value in values[method]:
                    if and_or[method] == 'or':
                        local = [a or b for a, b in zip(list(self.df[method] == value), local)]
                    else:
                        local = [a and b for a, b in zip(list(self.df[method] == value), local)]

            detect_slice[1] = np.multiply(detect_slice[1], local)
            detect_slice[0] = np.multiply(detect_slice[0], local)

        self._slicer = detect_slice

    def get_detector_actual_lanes(self):
        list_no_blanks = self.df.loc[self._slicer[1]].Detect_2_Actual_Lane.values
        return self.df.loc[self._slicer[0]].Detect_Actual_Lane.values, list_no_blanks

    def get_all_detectors(self):
        # Using RW_Detector_2 as my indexer because it is only filled in where valid
        list_no_blanks = self.df.loc[self._slicer[1]].Sumo_Detector_2.values
        return self.df.loc[self._slicer[0]].Sumo_Detector.values, list_no_blanks

    def get_detector_actual_pos(self):
        list_no_blanks = self.df.loc[self._slicer[1]].Detect_2_Actual_Distance.values
        return self.df.loc[self._slicer[0]].Detect_Actual_Distance.values, list_no_blanks

    def get_all_rw_ids(self):
        list_no_blanks = self.df.loc[self._slicer[1]].RW_Detector_2.values
        return self.df.loc[self._slicer[0]].RW_Detector.values, list_no_blanks

    def get_all_detector_indexes(self):
        list_no_blanks = self.df.loc[self._slicer[1]].Sumo_Detector_2.index.values
        return self.df.loc[self._slicer[0]].index.values, list_no_blanks

    def get_all_detector_edges(self):
        list_no_blanks = self.df.loc[self._slicer[1]].Detect_2_Actual_Edge.values
        return self.df.loc[self._slicer[0]].Detect_Actual_Edge.values, list_no_blanks

    def get_all_detector_information(self, slicer_method=None, slicer_value=None, and_or=None):
        self._set_slicer_locations(methods=slicer_method, values=slicer_value, and_or=and_or)
        detect1_lanes, detect2_lanes = self.get_detector_actual_lanes()
        detect1, detect2 = self.get_all_detectors()
        detect1_rw, detect2_rw = self.get_all_rw_ids()
        ind_1, ind_2 = self.get_all_detector_indexes()
        edge_1, edge_2 = self.get_all_detector_edges()
        main_detect = np.vstack((detect1, detect1_lanes, detect1_rw, edge_1, ind_1, [1] * len(detect1))).T
        secondary_detect = np.vstack((detect2, detect2_lanes, detect2_rw, edge_2, ind_2, [2] * len(detect2))).T
        return np.vstack((main_detect, secondary_detect))


