from cmd_parse import ParseCmd
import wifi
from machine import Pin,reset
import utime
print('###########################################')
ts = ParseCmd('test_cfg')
utime.sleep_ms(200)
if 'SmartConnent' in ts.dat:
    if ts.dat['SmartConnent'] == 1:
        ts.dat['SmartConnent'] = 0
        ts.updata_file()
        print('smartconnent')
        wifi.smartconfig()

if 'SafeMode' in ts.dat:
    if ts.dat['SafeMode'] == 1:
        ts.dat['SafeMode'] = 0
        ts.updata_file()
        print('now in SafeMode')
        print('connent')
        wifi.try_connect()
        import webrepl
        webrepl.start()

    else:
        print('start')
        while True:
            try:
                f=open('m.py', 'r')
                exec(f.read())
            except:
                f.close()
                reset()



