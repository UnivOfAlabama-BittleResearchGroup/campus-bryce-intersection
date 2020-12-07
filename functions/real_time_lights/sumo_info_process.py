
class DetectorProcess:

    def __init__(self, traci, IDS):

        self.traci = traci
        self.IDS = IDS
        self._hex_string_last = ""
        self._vehicle_ids = {_id: [] for _id in IDS[0]}

    def get_occupancy(self):
        binary_list = ["0"] * 8
        hex_string = None
        for i, ID in enumerate(self.IDS[0]):
            local_vehicle_ids = self.traci.lanearea.getLastStepVehicleIDs(ID)
            if sorted(local_vehicle_ids) != sorted(self._vehicle_ids[ID]):
                binary_list[8 - int(self.IDS[1][i])] = "1"
            self._vehicle_ids[ID] = local_vehicle_ids
            # if self.traci.lanearea.getLastStepVehicleNumber(ID) > 0:
            #     binary_list[8 - int(self.IDS[1][i])] = "1"
        if "1" in binary_list:
            detect_binary = "".join(binary_list)
            print(detect_binary)
            hex_string = '%0*X' % ((len(detect_binary) + 3) // 4, int(detect_binary, 2))
        # if self._hex_string_last == hex_string:
        #     hex_string = None
        # else:
        #     self._hex_string_last = hex_string
        return hex_string
