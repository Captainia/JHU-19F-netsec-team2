import sys, asyncio
import playground

from playground.network.protocols.vsockets import VNICDumpProtocol
from playground.network.protocols.packets.switching_packets import WirePacket

from cmdHandler import printx, printError,DataHandler
import json

# from playground.common.logging import EnablePresetLogging, PRESET_DEBUG
# EnablePresetLogging(PRESET_DEBUG)

class protocol_factory(VNICDumpProtocol):
    def __init__(self,loop):
        self.loop = loop

    # BUG: 
    # def super().connection_made(self,transport):
    #     printx("connection_made to {}".format(transport.get_extra_info("peername")))
    #     self.transport = transport

    def data_received(self,data):

        self.dataHandler = DataHandler(self.transport) # TODO: del this

        pkts = self.dataHandler.recvPktSaveFile(data)
        # # save ptk to json
        #     #jsonData = json.dump(pkts)
        #     #f.write(pkts)
        #     json.dump(pkts,f)

        for pkt in pkts:
            self.dataHandler.recvPktSaveFile(pkt.data)
            # TODO: do something

def main(args):

    loop = asyncio.get_event_loop()
    coro = playground.connect.raw_vnic_connection(lambda: protocol_factory(loop), vnicName="default")
    # coro = playground.connect.raw_vnic_connection(playground.connect.raw_vnic_connection(protocol_factory, vnic_name="default"))
    listener =  loop.run_until_complete(coro)

    # loop.set_debug(1)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    listener.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main(sys.argv[1:])
