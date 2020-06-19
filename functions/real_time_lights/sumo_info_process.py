
class DetectorProcess:

    def __init__(self, traci, IDS):

        self.traci = traci
        self.IDS = IDS
        self._binary_list_last = []

    def get_occupancy(self):
        binary_list = ["0"] * 8
        hex_string = None
        for i, ID in enumerate(self.IDS[0]):
            if self.traci.lanearea.getLastStepVehicleNumber(ID) > 0:
                binary_list[8 - int(self.IDS[1][i])] = "1"
                # print(f"Call to detector {self.IDS[1][i]}")
        # check if there was a difference since last time:
        #if set(binary_list) ^ set(self._binary_list_last):
        if "1" in binary_list:
            detect_binary = "".join(binary_list)
            # print(detect_on)
            # print('%0*X' % ((len(detect_on) + 3) // 4, int(detect_on, 2)))
            hex_string = '%0*X' % ((len(detect_binary) + 3) // 4, int(detect_binary, 2))
        self._binary_list_last = binary_list
        return hex_string

    # def __init__(self, IDS):
    #
    #     self.IDS = IDS
    #     self._binary_list_last = []
    #
    # def get_occupancy(self):
    #     binary_list = ["0"] * 8
    #     hex_string = None
    #     for i, ID in enumerate(self.IDS[0]):
    #         if traci.lanearea.getLastStepVehicleNumber(ID) > 0:
    #             binary_list[8 - int(self.IDS[1][i])] = "1"
    #             # print(f"Call to detector {self.IDS[1][i]}")
    #     # check if there was a difference since last time:
    #     #if set(binary_list) ^ set(self._binary_list_last):
    #     if "1" in binary_list:
    #         detect_binary = "".join(binary_list)
    #         # print(detect_on)
    #         # print('%0*X' % ((len(detect_on) + 3) // 4, int(detect_on, 2)))
    #         hex_string = '%0*X' % ((len(detect_binary) + 3) // 4, int(detect_binary, 2))
    #     self._binary_list_last = binary_list
    #     return hex_string



