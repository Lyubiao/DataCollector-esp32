from machine import Pin,WDT
import utime
import ubinascii
class connect():

    def __init__(self, uart):
        self.uart = uart
        self.RecvBuf = bytearray()

    def send(self, state):
        self.uart.write(state + '\r\n')

    def recv(self, func):
        recvlen = self.uart.any()
        if recvlen > 0:
            buffer = self.uart.read(recvlen)
            for data in buffer:
                self.RecvBuf.append(data)
            func(self.RecvBuf)


class device(connect):

    def __init__(self, rst, uart):
        connect.__init__(self, uart)
        self.rst = Pin(rst, Pin.OUT)
        self.sendstate = 0


    def reset(self):
        self.rst.value(1)
        utime.sleep_ms(150)
        self.rst.value(0)


class control(device):
    def __init__(self, rst, uart):

        device.__init__(self, rst, uart)

        self.state = ['idle', 'AT', 'AT+CIMI', 'AT+COPS=1,2,\"46000\"', 'AT+CSQ', 'AT+CEREG?', 'AT+CGATT?',
                      'AT+NSOCR="DGRAM",17,0,1', 'AT+NSOCFG=0', 'AT+NSOCFG=0,0,1', 'end']
        self.RecvMax = 128
        self.state_len = len(self.state)
        self.state_index = 0
        self.retrans_times = 0
        self.last_time = 0
        self.setup()
        self.is_setup = 0

    def is_out(self):
        if (len(self.RecvBuf) > self.RecvMax):
            print('out line')
            print('resend:', self.state[self.state_index])
            self.RecvBuf = bytearray()
            self.send(self.state[self.state_index])
            self.retrans_times += 1
            self.last_time = utime.ticks_ms()

    def transform(self):
        self.RecvBuf = bytearray()
        self.retrans_times = 0
        self.state_index += 1
        self.send(self.state[self.state_index])
        self.last_time = utime.ticks_ms()

    def sendto(self, addr, port, data):
        temp =  ubinascii.hexlify(bytearray(data))
        temp = str(temp, "utf8")
        data = 'AT+NSOST=0,%s,%s,%s,%s' % (addr, port,str(int(len(temp)/2)), temp)
        print(bytearray(data))
        self.send(data)
        self.sendstate = 1

    def check_ack(self, recvbuf, ack):
        return True if ack in recvbuf else False

    def configure(self, recvbuf):
        if (self.state[self.state_index] == 'AT' or self.state[self.state_index] == 'AT+CIMI' \
            or self.state[self.state_index] == 'AT+COPS=1,2,\"46000\"' or self.state[self.state_index] == \
            'AT+NSOCFG=0' or self.state[self.state_index] == 'AT+NSOCFG=0,0,1') and self.check_ack(recvbuf,
                                                                                                   b'\r\nOK\r\n'):
            print('cheak ok', recvbuf)
            self.transform()
        elif self.state[self.state_index] == 'AT+CSQ' and self.check_ack(recvbuf, b'\r\n+CSQ:'):
            print('cheak ok', recvbuf)
            strbuf = bytes(recvbuf)
            tem=strbuf.split(b'+CSQ:')
            tem= tem[1].split(b',')
            csq = int(tem[0])
            # print(csq)
            if csq > 12 and csq < 99:
                self.transform()
        elif self.state[self.state_index] == 'AT+CEREG?' and self.check_ack(recvbuf, b'+CEREG:0'):
            print('cheak ok', recvbuf)
            strbuf = bytes(recvbuf)
            index = strbuf.find(b'G:')
            reg = int(strbuf[index + 4:index + 5])
            if reg == 1 or reg == 5:
                self.transform()
        elif self.state[self.state_index] == 'AT+CGATT?' and self.check_ack(recvbuf, b'+CGATT:1'):
            print('cheak ok', recvbuf)
            self.transform()
        elif self.state[self.state_index] == 'AT+NSOCR="DGRAM",17,0,1' and self.check_ack(recvbuf, b'\r\nOK\r\n'):
            print('cheak ok', recvbuf)
            strbuf = bytes(recvbuf)
            index = strbuf.find(b'\r\nOK\r\n')
            reg = int(strbuf[index - 3]) - 48
            print(reg)
            if reg >= 0 and reg <= 6:
                self.transform()
        else:
            self.is_out()

    def setup(self):
        while True:
            self.recv(self.configure)
            if self.state[self.state_index] == 'idle':
                print('reset')
                self.reset()
                self.transform()
            if self.state[self.state_index] == 'end':
                print('end')
                break
            now_time = utime.ticks_ms()
            if self.last_time + 500 < now_time:
                self.RecvBuf = bytearray()
                self.retrans_times += 1
                if self.retrans_times >= 40:
                    self.retrans_times = 0
                    self.state_index = 0
                else:
                    print('retrans_times', self.retrans_times)
                    print('resend:', self.state[self.state_index])
                    self.send(self.state[self.state_index])
                    self.last_time = utime.ticks_ms()

class ZW_Net(control):
    import zhiwu
    import  cmd_parse

    A = zhiwu.encode(43, devid='1P-01-L1-DGLB')
    B = zhiwu.decode(55)
    fo = cmd_parse.ParseCmd('test_cfg')
    def __init__(self, rst, uart):
        control.__init__(self,rst,uart)
        self.wdt = WDT(0, 60 * 3)
    def recv_parse(self,recvbuf):
        print(recvbuf)
        if self.check_ack(recvbuf, b'\r\nERROR\r\n'):
            self.is_setup+=1
            print('et=',self.is_setup)
        if self.check_ack(recvbuf, b'219.222.189.98,9954'):
            self.wdt.feed()
            print('feed_______dog')
            recvbuf = bytes(recvbuf)
            buf = recvbuf.split(b',')
            # print(buf)
            index = buf.index(b'219.222.189.98')
            data_len = int(buf[index + 2])
            # print(data_len)
            num = recvbuf.find(buf[index])

            if data_len >= 0 and data_len < 10:
                rec = recvbuf[num + 22:num + 22 + data_len]
            elif data_len >= 10 and data_len < 100:
                rec = recvbuf[num + 23:num + 23 + data_len]
            elif data_len > 100:
                rec = recvbuf[num + 24:num + 24 + data_len]
            # print(rec)
            # print(len(rec))
            if data_len == len(rec):
                result = ZW_Net.B.parse(bytearray(rec))
                if result:
                    print(result)
                    self.sendstate = 0

                    if b':' in result[1]:
                        str = result[1].decode('utf-8')
                        Pack = ZW_Net.A.command((str))
                        try:
                            self.sendto('zwidas.top', '9954', Pack)
                            utime.sleep_ms(100)
                            ZW_Net.fo.analysis_cmd(str)
                        except Exception as e:
                            print(e)

            else:
                print('parse is error#################################################')
        self.RecvBuf = bytearray()


# from machine import UART
#
# uart = UART(2)
# uart.init(9600, bits=8, parity=None, stop=1)
# ts = ZW_Net(14, uart)
# print('finish')
#
# from machine import Timer
#
# tim = Timer(0)
# tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t: _send_data())
# ts.send('AT+CMEE=1')
# def _send_data():
#     global send
#     if send == 0:
#         send = 1
#     print('really')
#
#
# send = 0
# sync=0
#
# def send_data():
#     global send
#     global  sync
#     if sync==360:
#         sync=0
#     else:
#         sync+=1
#     if send == 1:
#         send = 0
#         Pack = ts.A.collect('ack', str(sync))
#         print('len=%d'%len(Pack))
#         ts.sendto('219.222.189.98', '9954', Pack)
#         utime.sleep_ms(100)
#
#
# def unit_test():
#     last_time = utime.ticks_ms()
#     while True:
#         send_data()
#         ts.recv(ts.recv_parse)
#         now_time=utime.ticks_ms()
#         if now_time-300>last_time:
#             last_time=now_time
#             ts.send('AT+NSORF=0,256')
#             utime.sleep_ms(100)
#             print('recv is response')
#             ts.RecvBuf = bytearray()
# if __name__=='__main__':
#     unit_test()