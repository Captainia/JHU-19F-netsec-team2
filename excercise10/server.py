import asyncio
import playground
import time
import sys
from cmdHandler import ServerCmdHandler, printx
from threading import Timer


# from playground.common.logging import EnablePresetLogging, PRESET_VERBOSE
# EnablePresetLogging(PRESET_VERBOSE)

PORT_NUM = 2222
timer = Timer()


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        timer = Timer()
        printx('Connection made')
        self.transport = transport  
        self.cmdHandler = ServerCmdHandler(transport)

        # NOTE:py3.7
        for a in self.cmdHandler.game.agents:
            asyncio.create_task(a)

        # NOTE:This is for py3.6
        # self.loop = asyncio.get_event_loop()
        # self.loop.create_task(asyncio.wait(
        #     [asyncio.ensure_future(a) for a in self.cmdHandler.game.agents]))

    def data_received(self, data):
        self.cmdHandler.serverRecvData(data)
    

def main(args):
    loop = asyncio.get_event_loop()
    coro = playground.create_server(
        ServerProtocol, "localhost", PORT_NUM)  
    server = loop.run_until_complete(coro)

    printx('Servering on{}'.format(server.sockets[0].getsockname()))
    # loop.set_debug(1)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
