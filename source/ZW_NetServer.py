import wifi

wifi.try_connect()

from XAsyncSockets import XAsyncSocketsPool, XAsyncUDPDatagram
from _thread import start_new_thread
import zhiwu
from cmd_parse import ParseCmd
from machine import Pin
recv_led=Pin(18,Pin.OUT)
class NetServer:
    Pool = None

    def __init__(self, Server=('0.0.0.0', 32)):
        if NetServer.Pool is None:
            NetServer.Pool = XAsyncSocketsPool()
            start_new_thread(NetServer.run_forever, ())

        self.UDPDatagram = XAsyncUDPDatagram.Create(NetServer.Pool, Server, 256)
        self.UDPDatagram.OnDataRecv = NetServer._onUDPDatagramDataRecv
        self.UDPDatagram.OnFailsToSend = NetServer._onUDPDatagramFailsToSend
        print("LocalAddr : %s:%s" % self.UDPDatagram.LocalAddr)

    def exit(self):
        self.UDPDatagram.Close()

    def unit_test(self):
        import time
        Remote = ('10.10.10.237', 9954)
        data = bytearray("123123")
        while True:
            self.UDPDatagram.AsyncSendDatagram(datagram=data, remoteAddr=Remote)
            print(data)
            time.sleep(2)

    def run_forever():
        try:
            NetServer.Pool.AsyncWaitEvents()
        finally:
            NetServer.Pool.StopWaitEvents()

    def _onUDPDatagramDataRecv(xAsyncUDPDatagram, remoteAddr, datagram):
        print('On UDP Datagram Data Recv (%s:%s) :' % remoteAddr, bytes(datagram), xAsyncUDPDatagram)

    def _onUDPDatagramFailsToSend(xAsyncUDPDatagram, datagram, remoteAddr):
        print('On UDP Datagram Fails To Send', bytes(datagram), remoteAddr, xAsyncUDPDatagram)


class DG_NetServer(NetServer):
    A = zhiwu.encode(43,devid='0P-0L-01-DGUT')
    B = zhiwu.decode(3)
    ts = ParseCmd('test_cfg')

    def __init__(self, file, Server=('0.0.0.0', 32)):
        if NetServer.Pool is None:
            NetServer.Pool = XAsyncSocketsPool()
            start_new_thread(NetServer.run_forever, ())

        self.UDPDatagram = XAsyncUDPDatagram.Create(DG_NetServer.Pool, Server, 256)
        self.UDPDatagram.OnDataRecv = DG_NetServer._onUDPDatagramDataRecv
        self.UDPDatagram.OnFailsToSend = DG_NetServer._onUDPDatagramFailsToSend
        print("LocalAddr : %s:%s" % self.UDPDatagram.LocalAddr)

    def unit_test(self):
        import time
        Remote = ('10.10.10.237', 9954)
        i = 0
        while True:
            time.sleep(2)
            i += 1
            if i == 30:
                i = 0
                zhiwu.set_time(0)
            self.sendto(('10.10.10.237', 9954), "temp", "123456")
            self.sendto(('10.10.10.237', 9954), "cheny", "123456")

    def sendto(self, Remote, source, data):
        # send_led.value(0) if send_led.value() else send_led.value(1)
        Pack = self.A.collect(source, data)
        # print('send the data')
        # print(bytearray(Pack))
        self.UDPDatagram.AsyncSendDatagram(datagram=bytearray(Pack), remoteAddr=Remote)

    def _onUDPDatagramDataRecv(xAsyncUDPDatagram, remoteAddr, datagram):
        recv_led.value(0) if recv_led.value() else recv_led.value(1)

        # print('recv:',bytes(datagram))
        result = DG_NetServer.B.parse(bytes(datagram))
        if result:
            print(result)
            # print('reserved')
            if b':' in result[1]:
                str = result[1].decode('utf-8')
                print(str)
                # Pack = DG_NetServer.A.command((str))
                # try:
                #     xAsyncUDPDatagram.AsyncSendDatagram(datagram=bytearray(Pack), remoteAddr=('219.222.189.98', 9954))
                DG_NetServer.ts.analysis_cmd(str)
                # except Exception as e:
                #     print(e)
        else:
            print('parse error')

if __name__ == '__main__':
    ZW_client = DG_NetServer('t_cfg')
    ZW_client.unit_test()
    ZW_client.exit()
