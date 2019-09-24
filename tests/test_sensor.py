import machine
i2c = machine.I2C('X')
machine.Pin.board.EN_3V3.value(1)
print("Scanning I2C Bus: {}".format(i2c.scan()))


class HDC2080:
    def __init__(self, i2c, addr=64):
        self.i2c = i2c
        self.addr = addr

    def is_ready(self):
        return self.i2c.readfrom_mem(self.addr, 0x0f, 1)[0] & 1 == 0

    def measure(self):
        self.i2c.writeto_mem(self.addr, 0x0f, b'\x01')

    def temperature(self):
        data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        data = data[0] | data[1] << 8
        return data / 0x10000 * 165 - 40

    def humidity(self):
        data = self.i2c.readfrom_mem(self.addr, 0x02, 2)
        data = data[0] | data[1] << 8
        return data / 0x10000 * 100

hdc = HDC2080(i2c)

while True:
    hdc.measure()
    while not hdc.is_ready():
        machine.idle()
    print(hdc.temperature(), hdc.humidity())
