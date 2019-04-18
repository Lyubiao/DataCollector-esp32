from machine import Pin, SPI
from micropython import const

class RN8302B():
    RN8302B_RMS_IA = const(0x0B)
    RN8302B_RMS_IB = const(0x0C)
    RN8302B_RMS_IC = const(0x0D)
    RN8302B_RMS_IN = const(0x0E)
    RN8302B_REG_GSIA = const(0x16)
    RN8302B_REG_GSIB = const(0x17)
    RN8302B_REG_GSIC = const(0x18)
    RN8302B_REG_GSIN = const(0x19)
    RN8302B_REG_WRITEANBLE = const(0x80)
    RN8302B_REG_WORKMODE = const(0x81)
    RN8302B_REG_MODSEL = const(0x86)
    RN8302B_CMD_WREN = const(0xE5)
    RN8302B_CMD_WRDIS = const(0xDC)
    RN8302B_CMD_GOEMM = const(0xA2)
    RN8302B_CMD_33 = const(0x33)
    RN8302B_CMD_34 = const(0x00)
    def __init__(self, spi, cs=2, rst=4):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.FLOAT24 = 16777216.0  # 2^24
        self.VOLTAGE_MULTIPLIER = (1 / self.FLOAT24 * 367)
        self.CURRENT_MULTIPLIER = (1 / self.FLOAT24 * 5)
        self.POWER_MULTIPLIER = (1 / self.FLOAT24 * 1.024 * 367 * 5 * 2)
        self.reset()
        self.start_up()

    def read(self, LowAdd, HighAdd, count):
        HighAdd = HighAdd * 16
        buf = bytearray(count + 1)
        self.cs.value(0)
        self.spi.write(bytearray([LowAdd]))
        self.spi.write(bytearray([HighAdd]))
        check = LowAdd + HighAdd
        self.spi.write_readinto(buf, buf)  # buf
        self.cs.value(1)
        for i in range(count):
            check = buf[i] + check
        check = bytearray([~check])

        if check[0] == buf[count]:
            # print('read successful')
            # for i in range(count + 1):
            #     print(buf[i])
            return buf
        else:
            print('read error')
            return None

    def write(self, LowAdd, HighAdd, Data, count):
        HighAdd = HighAdd * 16 + 0x80
        self.cs.value(0)
        self.spi.write(bytearray([LowAdd]))
        self.spi.write(bytearray([HighAdd]))
        check = LowAdd + HighAdd
        self.spi.write(Data)  # data
        for i in range(count):
            check += Data[i]
        # check = bytearray([~check])
        self.spi.write(bytearray([~check]))  # send check bit
        self.cs.value(1)
        # print(b[0], b[1], b[2])
        # print(check[0])
        # print(b[count])
        return 0

    def reset(self):
        import utime
        self.rst.value(0)
        utime.sleep_ms(500)
        self.rst.value(1)
        utime.sleep_ms(100)

    def start_up(self):
        import utime
        self.write(self.RN8302B_REG_WRITEANBLE, 1, bytearray([self.RN8302B_CMD_WREN]), 1)  # // 写使能
        # RN8302_Write_Reg(0x62, 0x0000ff, 3); // 通道使能
        self.write(self.RN8302B_REG_WORKMODE, 1, bytearray([self.RN8302B_CMD_GOEMM]), 1)  # // 工作模式
        self.write(self.RN8302B_REG_MODSEL, 1, bytearray([self.RN8302B_CMD_34]), 1)  # 三相四线

        # RN8302_Write_Reg(0x13, GSUA, 2); // Ua通道增益
        # RN8302_Write_Reg(0x14, GSUB, 2); // Ub通道增益
        # RN8302_Write_Reg(0x15, GSUC, 2); // UC通道增益
        # RN8302_Write_Reg(0x16, GSIA, 2); // Ia通道增益
        # RN8302_Write_Reg(0x17, GSIB, 2); // Ib通道增益
        # RN8302_Write_Reg(0x18, GSIC, 2); // Ic通道增益
        # PHSUA = G_EffectPar_Info.PHSUA;
        # PHSUB = G_EffectPar_Info.PHSUB;
        # PHSUC = G_EffectPar_Info.PHSUC;
        # RN8302_Write_Reg(0x0C, PHSUA, 1); // Ua相位校正
        # RN8302_Write_Reg(0x0D, PHSUB, 1); // Ub相位校正
        # RN8302_Write_Reg(0x0E, PHSUC, 1); // Uc相位校正
        self.write(self.RN8302B_REG_GSIA, 1, bytearray([0x06, 0x51]), 2)  # A相电流校正
        self.write(self.RN8302B_REG_GSIB, 1, bytearray([0x06, 0x51]), 2)  # B相电流校正
        self.write(self.RN8302B_REG_GSIC, 1, bytearray([0x06, 0x51]), 2)  # C相电流校正
        self.write(self.RN8302B_REG_GSIN, 1, bytearray([0x06, 0x51]), 2)  # N相电流校正
        self.read(self.RN8302B_RMS_IA, 0, 4)
        self.read(self.RN8302B_RMS_IB, 0, 4)
        self.read(self.RN8302B_RMS_IC, 0, 4)
        self.read(self.RN8302B_RMS_IN, 0, 4)
        utime.sleep_ms(100)

    def read_i(self, current_channal):
        current = self.read(current_channal, 0, 4)
        if current:
            temp = current[0] * 16777216 + current[1] * 65536 + current[2] * 256 + current[3]
            I = 160 * temp / 134217728
            return I
        else:
            return None


# rn8302b_write(0x82,1,0xFA, 1)#// 软件复位

def unit_test():
    import utime
    vspi = SPI(-1, polarity=0, phase=1, sck=Pin(5), mosi=Pin(23), miso=Pin(19), baudrate=200000)  # -1 software spi
    ts = RN8302B(vspi)



    while True:
        A = ts.read_i(ts.RN8302B_RMS_IA)
        B = ts.read_i(ts.RN8302B_RMS_IB)
        C = ts.read_i(ts.RN8302B_RMS_IC)
        N = ts.read_i(ts.RN8302B_RMS_IN)
        if A:
            print('current=%.1fA' % (A))
        if B:
            print('current=%.1fA' % (B))
        if C:
            print('current=%.1fA' % (C))
        if N:
            print('current=%.1fA' % (N))
        utime.sleep_ms(800)
    # rn8302b_read(0x16, 1, 2)
    # utime.sleep_ms(50)
    # rn8302b_write(0x16, 1, bytearray([0x06, 0x51]), 2)
    # utime.sleep_ms(50)
    # rn8302b_read(0x16, 1, 2)
    # utime.sleep_ms(50)


if __name__ == '__main__':
    unit_test()
