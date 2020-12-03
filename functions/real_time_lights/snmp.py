import time
import subprocess
from multiprocessing import Process, Queue, Event

oid_SET_DETECTOR_CALL = '1.3.6.1.4.1.1206.3.5.2.19.8.2.1'
oid_GET_GREEN_CALL = '1.3.6.1.4.1.1206.4.2.1.1.4.1.4.1'
oid_GET_YELLOW_CALL = '1.3.6.1.4.1.1206.4.2.1.1.4.1.3.1'
oid_asc3DataLogEnable = '1.3.6.1.4.1.1206.3.5.2.9.17.1'
GET_RATE = 0.5


def _get_states(ip, port):
    i = 0
    light_string = []
    for oid, color in [(oid_GET_GREEN_CALL, 'g'), (oid_GET_YELLOW_CALL, 'y')]:
        cmd_g = "".join(["snmpget -v 1 -c public ", str(ip), ":", str(port), " ", oid])
        returned_value_g = subprocess.check_output(cmd_g, shell=True)
        status = str(returned_value_g).split(':')[-1][:-5].strip()  # clean up the returned data
        bits = bin(int(status))[2:].zfill(8)[::-1]  # convert to bit string and flip the order
        if i < 1:
            light_string = ['r'] * len(bits)
        for i, bit in enumerate(bits):
            if bit == '1':
                light_string[i] = color
        i += 1
    return "".join(light_string)


def _threaded_get(ip, port, queue, event):
    last_results = "r" * 8
    while not event.is_set():
        light_string = _get_states(ip, port)
        if last_results != light_string:
            last_results = light_string
            actions = [(i+1, color) for i, color in enumerate(light_string)]
            queue.put(actions)
        time.sleep(GET_RATE)


class SNMP:

    def __init__(self, ip, port, light_control=False):
        self.IP = ip
        self.PORT = port

        if light_control:
            self._queue = Queue()
            self._kill_event = Event()
            self._p = self._spawn_mp()
            # self._t = self._spawn_threads()

    def kill_threads(self):
        self._kill_thread()

    def send_detectors(self, hex_string):
        print("sending ", hex_string)
        cmd_string = "".join(["snmpset -v 1 -c public ", str(self.IP), ":", str(self.PORT), " ",
                              oid_SET_DETECTOR_CALL, " x ", hex_string])
        subprocess.check_output(cmd_string.split())

    def _spawn_mp(self):
        p = Process(target=_threaded_get, args=(self.IP, self.PORT, self._queue, self._kill_event))
        p.start()
        return p

    def _spawn_threads(self):
        from threading import Thread
        t = Thread(target=_threaded_get, args=(self.IP, self.PORT, self._queue, self._kill_event))
        t.start()
        return t

    def _kill_thread(self):
        self._kill_event.set()
        self._p.join()

    def _check_threads(self):
        movements = []
        if not self._queue.empty():
            movements += self._queue.get()
        if movements:
            print(movements)
            return movements

    def get_light_states(self):
        return {'tl_1': self._check_threads()}

    def set_recording(self, state):
        # This doesn't work, will have to manually set
        value = 1 if state == 'enable' else 2
        cmd_string = "".join(["snmpset -v 1 -c public ", str(self.IP), ":", str(self.PORT), " ",
                              oid_asc3DataLogEnable, " x ", str(value)])
        subprocess.check_output(cmd_string.split())
