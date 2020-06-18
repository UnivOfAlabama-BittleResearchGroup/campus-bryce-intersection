# import socket
#
# IP = "127.0.0.1"
# PORT = 501
# BUFFERSIZE = 1024
#
#
# import logging
# import socket
# import time
#
# log = logging.getLogger('udp_server')
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# # def udp_server(host=IP, port=PORT):
# #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# #     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# #
# #     log.info("Listening on udp %s:%s" % (host, port))
# #     s.bind((host, port))
# #     while True:
# #         (data, addr) = s.recvfrom(128*1024)
# #         yield data
# #
# #
# # FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
# # logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)
# #
# # for data in udp_server():
# #     log.debug("%r" % (data,))
#
#
# while True:
#
#     TimetoLive = '1.3.6.1.4.1.1206.3.5.2.19.8.1.1'
#     Message = '1.3.6.1.4.1.1206.3.5.2.19.8.2.1 x 0x01'
#
#     sock.sendto(bytes(TimetoLive, "utf-8"), (IP, PORT))
#
#     sock.sendto(bytes(Message, "utf-8"), (IP, PORT))
#
#     time.sleep(1)

# from puresnmp import get
#
# COMMUNITY = 'p'
#

#
# OID = '1.3.6.1.4.1.1206.3.5.2.19.8.1.1'
#
# result = get(ip=IP, community=COMMUNITY, oid=OID, port=PORT)
#
# print('''Get Result:
#     Type: %s
#     repr: %s
#     str: %s
#     ''' % (type(result), repr(result), result))

# from pysnmp.hlapi import *
#
# errorIndication, errorStatus, errorIndex, varBinds = next(
#     getCmd(SnmpEngine(),
#            CommunityData('public', mpModel=0),
#            UdpTransportTarget((IP, PORT)),
#            ContextData(),
#            ObjectType(ObjectIdentity('1.3.6.1.4.1.1206.3.5.2.19.8.1.1')))
# )
#
# if errorIndication:
#     print(errorIndication)
# elif errorStatus:
#     print('%s at %s' % (errorStatus.prettyPrint(),
#                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
# else:
#     for varBind in varBinds:
#         print(' = '.join([x.prettyPrint() for x in varBind]))

# from pysnmp.hlapi import *
#
# next(
# setCmd(SnmpEngine(),
#            CommunityData('public', mpModel=0),
#            UdpTransportTarget((IP, PORT)),
#            ContextData(),
#            ObjectType(ObjectIdentity('1.3.6.1.4.1.1.1206.4.2.1.1.4'),)
# )
# )
#
# if errorIndication:
#     print(errorIndication)
# elif errorStatus:
#     print('%s at %s' % (errorStatus.prettyPrint(),
#                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
# else:
#     for varBind in varBinds:
#         print(' = '.join([x.prettyPrint() for x in varBind]))

# from easysnmp import snmp_get, snmp_set, snmp_walk
#
# # Grab a single piece of information using an SNMP GET
# snmp_get('sysDescr.0', hostname='localhost', community='public', version=1)

IP = "127.0.0.1"
PORT = 501
BUFFERSIZE = 1024

from pysnmp.hlapi import *

errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData('public', mpModel=0),
           UdpTransportTarget((IP, PORT)),
           ContextData(),
           ObjectType(ObjectIdentity('1.3.6.1.4.1.1.1206.4.2.1.1.4.1.10')))
)

if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
else:
    for varBind in varBinds:
        print(' = '.join([x.prettyPrint() for x in varBind]))