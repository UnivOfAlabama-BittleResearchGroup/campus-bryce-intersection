from pysnmp.hlapi import *

oid_SET_DETECTOR_CALL = '1.3.6.1.4.1.1206.3.5.2.19.8.2.1'


class SNMP:

    def __init__(self, ip, port):

        self.IP = ip
        self.PORT = port

        # Instantating all of these once. They don't change between set/getCmd calls
        self.UDP_TRANSPORT_TARGET = UdpTransportTarget((self.IP, self.PORT))
        self.SNMP_ENGINE = SnmpEngine()
        self.COMMUNITY_DATA = CommunityData('public', mpModel=0)
        self.CONTEXT_DATA = ContextData()

    def send_detectors(self, hex_string):
        print("sending ", hex_string)

        next(
            setCmd(self.SNMP_ENGINE,
                   self.COMMUNITY_DATA,
                   self.UDP_TRANSPORT_TARGET,
                   self.CONTEXT_DATA,
                   ObjectType(ObjectIdentity(oid_SET_DETECTOR_CALL),
                              OctetString(hexValue=hex_string)
                              )
                   )
        )