from lxml import etree
import numpy as np
import pandas as pd
import csv


class ParseDetectorXML:

    fields = ['interval_begin', 'interval_end', 'interval_flow', 'interval_harmonicMeanSpeed', 'interval_id',
              'interval_length', 'interval_nVehContrib', 'interval_nVehEntered', 'interval_occupancy',
              'interval_meanSpeed']

    e2_fields = ['interval_begin',
                 'interval_end',
                 'interval_id',
                 'interval_sampledSeconds',
                 'interval_nVehEntered',
                 'interval_nVehLeft',
                 'interval_nVehSeen',
                 'interval_meanSpeed',
                 # 'interval_meanTimeLoss',
                 # 'interval_meanOccupancy',
                 # 'interval_maxOccupancy',
                 # 'interval_meanMaxJamLengthInVehicles',
                 # 'interval_meanMaxJamLengthInMeters',
                 # 'interval_maxJamLengthInVehicles',
                 # 'interval_maxJamLengthInMeters',
                 # 'interval_jamLengthInVehiclesSum',
                 # 'interval_jamLengthInMetersSum',
                 # 'interval_meanHaltingDuration',
                 # 'interval_maxHaltingDuration',
                 # 'interval_haltingDurationSum',
                 # 'interval_meanIntervalHaltingDuration',
                 # 'interval_maxIntervalHaltingDuration',
                 # 'interval_intervalHaltingDurationSum',
                 # 'interval_startedHalts',
                 # 'interval_meanVehicleNumber',
                 # 'interval_maxVehicleNumber'
                 ]

    fields_simp = [col_name.split(sep="_")[-1] for col_name in fields]
    fields_simp[-1] = 'speed' # fixes the meanSpeed vs speed difference
    e2_fields_simp = [col_name.split(sep="_")[-1] for col_name in e2_fields]

    def __init__(self):
        self.data = []

    def parse_to_array(self, elem, fields):
        try:
            self.data.append([elem.attrib[key] for key in fields])
        except KeyError:
            return 0

    def parse_and_write(self, elem, fields):
        try:
            self._csv_writer.writerow([elem.attrib[key] for key in fields])
        except KeyError:
            return 0

    def fast_iter(self, context, func, fields):
        for event, elem in context:
            func(elem, fields)
            elem.clear()
            while elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    break
        del context

    def main(self, file_path, save_path=None, detect_type='e2'):

        header_fields = self.fields if detect_type == 'e1' else self.e2_fields
        fields = self.fields_simp if detect_type == 'e1' else self.e2_fields_simp

        context = etree.iterparse(file_path, events=("start", "end"))

        if save_path:
            with open(save_path, mode='w+') as file:
                self._csv_writer = csv.writer(file, delimiter=',')
                self._csv_writer.writerow(header_fields)
                self.fast_iter(context, func=self.parse_and_write, fields=fields)
        else:
            self.fast_iter(context, func=self.parse_to_array, fields=fields)
            return pd.DataFrame(np.array(self.data), columns=header_fields)
