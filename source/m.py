from cs5460a import cs5460a
from machine import SPI, Pin, Timer
from machine import UART
from m5310a import ZW_Net
import dht, machine
# import micropython
import gc
import utime
from ucollections import deque

dht = dht.DHT11(machine.Pin(33))
Relay = machine.Pin(26, machine.Pin.OUT)
pmos = machine.Pin(21, machine.Pin.OUT)
pmos.value(0)
power_io = machine.Pin(22, machine.Pin.IN)
Relay.value(0)
vspi = SPI(-1, sck=Pin(5), mosi=Pin(23), miso=Pin(19), baudrate=2000000)
driver = cs5460a(vspi)

data_cache = ()
DataCache = deque(data_cache, 15)
timeout = 0
sync = 0
count = 0
sendtime = 0
temp = 0


def creat_heart():
    global sync
    global DataCache
    sync += 1
    if sync >= 360:
        sync = 0
    print('sync=%d'%sync)
    pack = ts.A.collect('ack', str(sync))
    DataCache.append(pack)


def timetosend():
    global timeout
    global count
    if timeout == 0:
        timeout = 1
    count+=1
    print('really')


def send_data():
    global sendtime
    global temp
    while True:
        if len(DataCache):
            print(len(DataCache))
            # print(micropython.mem_info())
            if ts.sendstate == 0:
                sendtime = utime.ticks_ms()
                ts.sendstate = 1
                temp = DataCache.popleft()
                with lock:
                    ts.sendto('219.222.189.98', '9954', temp)
                    utime.sleep_ms(100)
                print('send_data=%s' % (bytearray(temp)))
                print('send_data___________________')
                gc.collect()
            else:
                if utime.ticks_ms() - sendtime > 10000:
                    sendtime = utime.ticks_ms()
                    ts.sendstate = 0
                    # with lock:
                    #     ts.sendto('219.222.189.98', '9954', temp)
                    #     utime.sleep_ms(100)
                    # print('send_data=%s' % (bytearray(temp)))
                    # print('re______send_data___________________')
        utime.sleep_ms(100)
def creat_data():
    u=driver.read_u()
    if u:
        pack = ts.A.collect('volalite', str('%.1f'%u))
        DataCache.append(pack)
    i=driver.read_i()
    if i:
        pack = ts.A.collect('current', str('%.1f'%i))
        DataCache.append(pack)
    p=driver.read_p()
    if p:
        pack = ts.A.collect('power', str('%.1f'%p))
        DataCache.append(pack)

    dht.measure()
    t=dht.temperature()
    h=dht.humidity()
    if h:
        pack = ts.A.collect('humi', str('%.1f'%h))
        DataCache.append(pack)
    if t:
        pack = ts.A.collect('temp', str('%.1f'%t))
        DataCache.append(pack)
    if Relay.value():
        pack = ts.A.collect('switch', str(1))
    else:
        pack = ts.A.collect('switch', str(0))
    DataCache.append(pack)

uart = UART(2)
uart.init(9600, bits=8, parity=None, stop=1)
ts = ZW_Net(14, uart)

pmos.value(1)
ts.send('AT+CMEE=1')
last_time = utime.ticks_ms()
from  _thread import start_new_thread,allocate_lock
lock = allocate_lock()

start_new_thread(send_data,())

tim = Timer(0)
tim.init(period=10000, mode=Timer.PERIODIC, callback=lambda t: timetosend())

while True:

    if power_io.value() == False:
        pmos.value(1)
        for i in range(3):
            utime.sleep_ms(5000)
            Pack = ts.A.collect('error', '01')
            with lock:
                ts.sendto('219.222.189.98', '9954', Pack)
            print('error_____________________')
        pmos.value(0)
    if ts.is_setup >= 15:
        ts.state_index = 0
        ts.is_setup = 0
        ts.setup()
    if timeout == 1:
        print(' ------------------%d' % Relay.value())
        timeout = 0
        creat_heart()

    if count==9:
        count=0
        creat_data()
    ts.recv(ts.recv_parse)
    now_time = utime.ticks_ms()
    if now_time - 300 > last_time:
        last_time = now_time
        with lock:
            ts.send('AT+NSORF=0,256')
            utime.sleep_ms(300)
        ts.RecvBuf = bytearray()
