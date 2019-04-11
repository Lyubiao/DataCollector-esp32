class ParseCmd():
    def __init__(self, file,relaypin=26):
        from machine import Pin
        self.dat = {}
        self.file = file
        self.relay = Pin(relaypin,Pin.OUT)
        self.read_file()

    def updata_file(self):
        with open(self.file + '.py', "w") as f:
            keys = list(self.dat.keys())
            # print(keys)
            for key in keys:
                f.write('{} = {}\n'.format(key, self.dat[key]))

    def read_file(self):
        try:
            __import__(self.file)
            print('import ok')
        except:
            default = "SafeMode = 0 \nMaxU = 250 \nMinU = 200 " \
                      "\nMaxI = 10 \nMinI = 0 \nTAlarm = 50 \nSmartConnent = 0\nswitch = 0 "
            print("create default test_cfg.py : \n" + default)
            with open(self.file + '.py', "w") as f:
                f.write(default)
        with open((self.file + '.py'), "r+") as f:
            for line in f:
                conv = line.strip().split(' = ')
                self.dat[conv[0]] = float(conv[1])

    def analysis_cmd(self,cmd_str):
        if ':' in cmd_str:
            num = cmd_str.find(':')
            key = str(cmd_str[:num])
            value = float(cmd_str[num + 1:])
            if key in self.dat:
                print('in dict')
                self.dat[key] = value
                if key == 'SafeMode':
                    if self.dat['SafeMode'] == 1:
                        # print('write file')
                        self.updata_file()
                        from machine import reset
                        reset()
                if key == 'switch':
                    if self.dat['switch'] == 1:
                        print('switch=1___________')
                        self.relay.value(1)
                    if self.dat['switch'] == 0:
                        self.relay.value(0)
                        print('switch=0___________')
                    self.updata_file()

def unit_test():
    ts = ParseCmd('t_cfg')
    print(ts.dat)
    ts.dat['SafeMode'] = 10
    ts.dat['MinI'] = 10
    ts.dat['switch'] = 1
    ts.updata_file()
    ts.read_file()
    print(ts.dat)
    with open('t_cfg.py', "r") as f:
        print(f.read())


if __name__ == '__main__':
    unit_test()
