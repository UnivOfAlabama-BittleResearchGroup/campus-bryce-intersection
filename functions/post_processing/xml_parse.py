from lxml import etree
import numpy as np
import pandas as pd
import time
import csv


class parse_detector_xml:

    fields = ['interval_begin', 'interval_end', 'interval_flow', 'interval_harmonicMeanSpeed', 'interval_id',
              'interval_length', 'interval_nVehContrib', 'interval_nVehEntered', 'interval_occupancy', 'interval_speed']

    fields_simp = [col_name.split(sep="_")[-1] for col_name in fields]

    def parse_and_write(self, elem):
        try:
            self._csv_writer.writerow([elem.attrib[key] for key in self.fields_simp])
        except KeyError:
            return 0


    def fast_iter(self, context, func):
        for event, elem in context:
            func(elem)
            elem.clear()
            while elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    break
        del context

    def main(self, file_path, save_path):
        context = etree.iterparse(file_path, events=("start", "end"))
        with open(save_path, mode='w+') as file:
            self._csv_writer = csv.writer(file, delimiter=',')
            self._csv_writer.writerow(self.fields)
            self.fast_iter(context, func=self.parse_and_write)


def parse_tl_xml(file_path, save_path):
    fields = ['tlLogic_id', 'tlLogic_programID', 'tlLogic_type', 'phase_duration', 'phase_state']
    data = []
    context = etree.iterparse(file_path, events=("start", "end"))
    for element in context:

        if element[1].tag == 'tlLogic':
            if len(element[1].attrib) == 3:
                meta_data = [element[1].attrib['id'], element[1].attrib['programID'], element[1].attrib['type']]
        elif element[1].tag == 'phase':
            if len(element[1].attrib) >= 2:
                data.append(meta_data + [element[1].attrib['duration'], element[1].attrib['state']])

        element[1].clear()

    pd.DataFrame(data=np.array(data), columns=fields).to_csv(save_path, index=False)


class parse_emissions_xml:

    fields = ['timestep_time',
              'vehicle_CO',
              'vehicle_CO2',
              'vehicle_HC',
              'vehicle_NOx',
              'vehicle_PMx',
              'vehicle_angle',
              'vehicle_eclass',
              'vehicle_electricity',
              'vehicle_fuel',
              'vehicle_id',
              'vehicle_lane',
              'vehicle_noise',
              'vehicle_pos',
              'vehicle_route',
              'vehicle_speed',
              'vehicle_type',
              'vehicle_waiting',
              'vehicle_x',
              'vehicle_y']

    col_name_split = [col_name.split(sep="_")[-1] for col_name in fields]


    def parse_and_write(self, elem):
        meta_data = [0]
        if (elem.tag == 'timestep') and (len(elem.attrib) > 0):
            meta_data = [elem.attrib['time']]
        elif (elem.tag == 'vehicle') and (len(elem.attrib) >= 19):
            self._csv_writer.writerow(meta_data + [elem.attrib[col_name] for col_name in
                                                   self.col_name_split[1:]])

    def fast_iter(self, context, func):
        for event, elem in context:
            func(elem)
            elem.clear()
            while elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    break
        del context

    def main(self, file_path, save_path):
        context = etree.iterparse(file_path, events=("start", "end"))
        with open(save_path, mode='w+') as file:
            self._csv_writer = csv.writer(file, delimiter=',')
            self._csv_writer.writerow(self.fields)
            self.fast_iter(context, func=self.parse_and_write)

    # print("writing to csv")
    # pd.DataFrame(data=np.array(data), columns=fields).to_csv(save_path, index=False)

#
# t1 = time.time()
# parse_emissions_xml(
#     '/home/max/Documents/US69_project/US69/03_sim_files/emissions/2020-04-06-13-21-11_OUTPUT_emissions.xml', 'data.csv')
# print("Finished in {} seconds".format(time.time() - t1))
