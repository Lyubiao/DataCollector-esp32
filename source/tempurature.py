# ############温度传感器测试###################################
Tp = 273.15
T = Tp + 25  # Normal Temperature Parameters
_T = 1 / T
B = 3950


class Temperature:

    def __init__(self, adc):
        self.adc = adc

    def value(self):
        adc_val = self.adc.read()
        Vout = (adc_val) * 3.9 / 4095.0
        # print(Vout)
        if 0 < Vout and Vout < 3.9:  # -26.9 and 160.5
            Rt = int(((3.28 / Vout) - 1)*51)/100  # Sampling Resistance is 5.1K ohm * 51 / self.R
            # print(Rt)
            import math
            T1 = 1 / (_T + math.log(Rt) / B) - Tp
            return round(T1, 1)
        print('ADC Value Error!')
        return None

class Temp():

    def __init__(self,pin):
        from machine import ADC, Pin
        self.adc = ADC(Pin(pin, Pin.IN))
        self.adc.atten(ADC.ATTN_11DB)  # 0-3.9V
    def value(self):
        adc_val = self.adc.read()
        Vout = (adc_val) * 3.9 / 4095.0
        if 0 < Vout and Vout < 3.9:  # -26.9 and 160.5
            Rt = int(((3.28 / Vout) - 1)*51)/100  # Sampling Resistance is 5.1K ohm * 51 / self.R
            # print(Rt)
            import math
            T1 = 1 / (_T + math.log(Rt) / B) - Tp
            return T1
        print('ADC Value Error!')
        return None


def unit_test():
    ta = Temp(35)
    tb = Temp(35)
    tc = Temp(32)
    tn = Temp(33)
    import utime
    while True:
        utime.sleep_ms(1000)
        print('ta=',ta.value())
        utime.sleep_ms(50)
        print('tb=',tb.value())
        utime.sleep_ms(50)
        print('tc=',tc.value())
        utime.sleep_ms(50)
        print('tn=',tn.value())
        utime.sleep_ms(50)
    # from machine import ADC, Pin
    # from time import sleep
    # adc1 = ADC(Pin(33))
    # adc2 = ADC(Pin(32))
    # adc1.atten(ADC.ATTN_11DB)  # 0-3.9V
    # adc2.atten(ADC.ATTN_11DB)  # 0-3.9V
    # temp1 = Temperature(adc1)
    # temp2 = Temperature(adc2)
    # while True:
    #     print('temp1=',temp1.value())
    #     print('temp2=',temp2.value())
    #     sleep(1)


if __name__ == '__main__':
    unit_test()
