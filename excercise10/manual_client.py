import asyncio
import playground
import sys

from autograder_ex8_packets import *
from cmdHandler import ClientCmdHandler, printx
from class_packet import *
# from playground.common.logging import EnablePresetLogging, PRESET_DEBUG
# EnablePresetLogging(PRESET_DEBUG)

IPADDR = "20191.2.57.98"
PORT = 2222


class ClientProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop

    def connection_made(self, transport):
        printx("Connection made!")
        self.transport = transport
        self.cmdHandler = ClientCmdHandler(transport)
        self.cmdHandler.sendGameInitRequestPkt()
        # send init pkt

    def data_received(self, data):
        self.cmdHandler.clientRecvData(data)

    def connection_lost(self, exc):
        printx('The server closed the connction')
        printx('Stop the event loop')
        self.loop.stop()


def main(args):
    loop = asyncio.get_event_loop()
    coro = playground.create_connection(lambda: ClientProtocol(loop=loop),
                                        IPADDR, PORT)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main(sys.argv[1:])
