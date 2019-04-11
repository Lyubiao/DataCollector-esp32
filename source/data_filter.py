try:
    __import__ ('test_cfg')

    print('import ok')
except:
    print('import error')
class DataFilter():
    def __init__(self, length=10):
        self.dat = [0] * length
        self.length = length
        self.count = 0
        self.is_send = 0
        self.Alarm = 0
        self.nowvalue = 0

    def set_length(self, length):
        if length > self.length:
            for num in range(length - self.length):
                self.dat.append(0)
        self.length = length

    def write(self, data):
        self.dat[self.count] = data
        self.count += 1
        self.is_send = 0
        self.Alarm = 0


class CurrentFilter(DataFilter):
    def set_alarmvalue(self, mini, maxi):
        self.MaxI = maxi
        self.MinI = mini

    def __init__(self, mini, maxi, length=10):
        DataFilter.__init__(self, length)
        self.set_alarmvalue(mini, maxi)

    def process(self, data):
        self.write(data)
        sum = 0
        if self.count == self.length:
            for num in self.dat:
                # print(num)
                sum = sum + num
            self.nowvalue = sum / self.length
            if self.nowvalue >= self.MaxI or self.nowvalue < self.MinI:
                self.Alarm = 1
            self.is_send = 1
            self.count = 0


class TempFilter(DataFilter):
    def set_alarmvalue(self, TAlarm):
        self.TAlarm = TAlarm

    def __init__(self, TAlarm, length=10):
        DataFilter.__init__(self, length)
        self.set_alarmvalue(TAlarm)

    def process(self, data):
        self.write(data)
        sum = 0
        if self.count == self.length:
            for num in self.dat:
                # print(num)
                sum = sum + num
            self.nowvalue = sum / self.length
            if self.nowvalue >= self.TAlarm:
                self.Alarm = 1
            self.is_send = 1
            self.count = 0


class VolatileFilter(DataFilter):
    def set_alarmvalue(self, minu, maxu):
        self.MaxU = maxu
        self.MinU = minu

    def __init__(self, minu, maxu, length=10):
        DataFilter.__init__(self, length)
        self.set_alarmvalue(minu, maxu)

    def process(self, data):
        self.write(data)
        sum = 0
        if self.count == self.length:
            for num in self.dat:
                # print(num)
                sum = sum + num
            self.nowvalue = sum / self.length
            if self.nowvalue >= self.MaxU or self.nowvalue < self.MinU:
                self.Alarm = 1
            self.is_send = 1
            self.count = 0

class PowerFilter(DataFilter):
    def set_alarmvalue(self, Palarm):
        self.Palarm = Palarm

    def __init__(self, Palarm, length=10):
        DataFilter.__init__(self, length)
        self.set_alarmvalue(Palarm)

    def process(self, data):
        self.write(data)
        sum = 0
        if self.count == self.length:
            for num in self.dat:
                # print(num)
                sum = sum + num
            self.nowvalue = sum / self.length
            if self.nowvalue >= self.Palarm :
                self.Alarm = 1
            self.is_send = 1
            self.count = 0


def creat_softdata():
    import random
    temp = random.randint(10, 24) + random.random()
    return temp

def unit_test():
    ts = TempFilter(18,length=5)
    for i in range(50):
        import utime
        utime.sleep_ms(300)
        ts.process(creat_softdata())
        if ts.is_send == 1:
            if ts.Alarm == 1:
                print('warming',ts.nowvalue)
            else:
                print('normal',ts.nowvalue)
    ts.set_length(15)
    ts.set_alarmvalue(16)
    print('###############')
    while True:
        utime.sleep_ms(300)
        ts.process(creat_softdata())
        if ts.is_send == 1:
            if ts.Alarm == 1:
                print('warming', ts.nowvalue)
            else:
                print('normal', ts.nowvalue)


if __name__ == '__main__':
    unit_test()
