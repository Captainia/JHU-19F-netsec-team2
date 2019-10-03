import sys
sys.path.insert(1, '../BitPoints-Bank-Playground3/src/')
import getpass
import playground
from OnlineBank import BankClientProtocol, OnlineBankConfig
from CipherUtil import loadCertFromFile
from playground.network.packet import PacketType
import os
import time
import asyncio

# NOTE: local pkts and files
from escape_room_010 import EscapeRoomGame # from escape_room_006 import EscapeRoomGame 
from autograder_ex8_packets import * 
from class_packet import *


E6_STRS = ["look mirror",
           "get hairpin",
           'unlock chest with hairpin',
           'open chest',
           'look in chest',
           'get hammer in chest',
           "hit flyingkey with hammer",
           "get key",
           "unlock door with key",
           "open door"]

# bank params
BANK_CERT_FILE_NAME = "20194_online_bank.cert"
MY_UNAME = "xma39"
MY_ACCOUNT = "xma39_account"
AMOUNT = 10
TEST_UNAME = "test"  # TODO:make sure of this

# for formatting print
FL = 7
SL = 20

def printx(string):
    print(string.center(80, '-')+'\n')


def printError(string):
    print(string.center(80, '!')+'\n')


class BankManager:
    def __init__(self):
        bankconfig = OnlineBankConfig()
        self.bank_addr = bankconfig.get_parameter("CLIENT", "bank_addr")
        self.bank_port = int(bankconfig.get_parameter("CLIENT", "bank_port"))
        # bank_stack = bankconfig.get_parameter("CLIENT", "stack", "default")
        self.bank_username = bankconfig.get_parameter("CLIENT", "username")
        self.certPath = os.path.join(
            bankconfig.path(), BANK_CERT_FILE_NAME)
        self.bank_cert = loadCertFromFile(self.certPath)
        self.bank_client = None

    async def connectToBank(self):
        if self.bank_client == None:
            self.setBankClient()
        await playground.create_connection(
            lambda: self.bank_client,
            self.bank_addr,
            self.bank_port,
            family='default'
        )
        printx("bank manager connected to bank with username: {}".format(
            self.bank_client._BankClientProtocol__loginName))

    def setBankClient(self):
        password = getpass.getpass(
            "Enter password for {}: ".format(self.bank_username))
        self.bank_client = BankClientProtocol(
            self.bank_cert, self.bank_username, password)

    async def transfer(self, src, dst, amount, memo):
        # preset
        await self.connectToBank()

        # 1. bank_client login
        try:
            await self.bank_client.loginToServer()
        except Exception as e:
            printError("Login error. {}".format(e))
            return (None, None)

        # 2. bank_client swtch account
        try:
            await self.bank_client.switchAccount(MY_ACCOUNT)
        except Exception as e:
            printError(
                "Could not set source account as {} because {}".format(src, e))
            return (None, None)

        # 3. get transfer result
        try:
            result = await self.bank_client.transfer(dst, amount, memo)
        except Exception as e:
            printError("Could not transfer because {}".format(e))
            return (None, None)

        return (result.Receipt, result.ReceiptSignature)


class ClientCmdHandler:
    def __init__(self, transport, pkt=None):
        self.dataHandler = DataHandler(transport)
        self.cmd_num = 0
        self.pkt = pkt
        if(self.pkt != None):
            self.dataHandler.sendPkt(pkt)
        self.bankManager = BankManager()

    def clientRecvData(self, data):
        pkts = self.dataHandler.recvPkt(data)
        for pkt in pkts:
            self.handleClientPkt(pkt)

    def handleClientPkt(self, pkt):
        pktID = pkt.DEFINITION_IDENTIFIER
        # 1: respond to auto grade submit pkt, request start game
        if pktID == AutogradeTestStatus.DEFINITION_IDENTIFIER:
            if pkt.client_status == 1:
                return
            self.sendGameInitRequestPkt()

        # 2: respond to game payment request, make payment
        elif pktID == GameRequirePayPacket.DEFINITION_IDENTIFIER:
            id, account, amount = process_game_require_pay_packet(pkt)
            asyncio.create_task(
                self.sendGamePaymentResponsePkt(id, account, amount))

        # 3: respond to game response, send game cmd
        elif pktID == GameResponsePacket.DEFINITION_IDENTIFIER:
            cmd = pkt.response  # BUG

            if E6_STRS[self.cmd_num] == "hit flyingkey with hammer":
                # wait until key moves to the wall
                if(cmd.split(' ')[-1] == 'wall'):
                    self.sendGameCmdPkt()
            else:
                self.sendGameCmdPkt()
        else:
            printx("unknown pkt recived:" + pktID)

    def sendGameInitRequestPkt(self):
        pkt = create_game_init_packet(TEST_UNAME)
        self.dataHandler.sendPkt(pkt)

    async def sendGamePaymentResponsePkt(self, id, account, amount):
        # check amount
        if(amount > 10):
            printx("the amount is "+amount +
                   ", which is over 10, so stop the process")
            return

        receipt, receipt_sig = await self.bankManager.transfer(MY_ACCOUNT, account, amount, id)

        # check transactoin
        if(receipt == None or receipt_sig == None):
            printError(
                "the bank transaction didn't complete, so the process stopped")
            return

        pkt = create_game_pay_packet(receipt, receipt_sig)
        self.dataHandler.sendPkt(pkt)

    def sendGameCmdPkt(self):
        if self.cmd_num + 1 > len(E6_STRS):
            return
        self.dataHandler.sendPkt(GameCommandPacket(
            command=E6_STRS[self.cmd_num]))  
        self.cmd_num += 1


class ServerCmdHandler:
    def __init__(self, transport):
        self.dataHandler = DataHandler(transport)
        self.cmd_num = 0
        self.game = EscapeRoomGame(output=self.sendGameResPkt)
        self.game.create_game()
        self.payStatus = False

    def serverRecvData(self, data):
        pkts = self.dataHandler.recvPkt(data)
        for pkt in pkts:
            self.handleServerPkt(pkt)
        if self.game.status == "escaped":
            self.payStatus = False
            printx('Student server side finished!')

    def handleServerPkt(self, pkt):
        pktID = pkt.DEFINITION_IDENTIFIER
        # 1: respond to game init pkt, ask payment
        if pktID == GameInitPacket.DEFINITION_IDENTIFIER:
            self.sendGamePaymentRequestPkt()

        # 2: respond to game payment response pkt, confirm payment
        elif pktID == GamePayPacket.DEFINITION_IDENTIFIER:
            receipt, receipt_sig = process_game_pay_packet(pkt)
            if(self.checkPayment(receipt, receipt_sig)):
                printx("payment confirmed")
                # if passed
                self.payStatus = True
                self.game.start()
            else:
                printx("payment confirm failed")

        # 3: respond to game command pkt, send game response
        elif pktID == GameCommandPacket.DEFINITION_IDENTIFIER:
            if self.payStatus:
                self.game.command(pkt.command)
                time.sleep(0.25)
            else:
                printError(
                    "client try to play game before the payment is confirmed!")

        else:
            printx("unknown pkt:" + pktID)

    def sendGamePaymentRequestPkt(self):
        pkt = create_game_require_pay_packet(MY_UNAME, MY_ACCOUNT, AMOUNT)
        self.dataHandler.sendPkt(pkt)

    def checkPayment(self, receipt, receipt_sig):
        # TODO: check payment, and return true if payment confirmed
        return True

    def sendGameResPkt(self, string):
        pkt = create_game_response(string, self.game.status)
        self.dataHandler.sendPkt(pkt)


class DataHandler:
    def __init__(self, transport):
        self.t = transport
        self.deserializer = PacketType.Deserializer()

    def sendPkt(self, pkt):
        pktBytes = pkt.__serialize__()
        self.t.write(pktBytes)
        self.printSent(pkt.DEFINITION_IDENTIFIER)
        self.printPkt(pkt)

    def recvPkt(self, data):
        self.deserializer.update(data)
        pkts = []
        for pkt in self.deserializer.nextPackets():
            self.printRecv(pkt.DEFINITION_IDENTIFIER)
            self.printPkt(pkt)
            pkts.append(pkt)
        return pkts

    def printSent(self, string):
        print("sent:".ljust(FL)+string)

    def printRecv(self, string):
        print('recv:'.ljust(FL)+string)

    def printPkt(self, pkt):
        for field in pkt.FIELDS:
            fName = field[0]
            print("".ljust(FL)+fName.ljust(SL) +
                  str(pkt._fields[fName]._data))
        print('\n')
