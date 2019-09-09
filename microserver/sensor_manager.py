"""
MIT License
Copyright (c) 2019 Samsung. n.herriot@samsung.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import pyb, time, drivers.sr_501_sensor
from micropython import const
from machine import Pin, I2C

from drivers.ssd1306 import SSD1306_I2C             # Used to control the OLED display
from drivers.sr_501_sensor import PIR               # Used to control the PIR Sensor
#from drivers.sr_501_sensor import simple_test_callback
from drivers.rcwl_0516_sensor import MicrowaveRadar # Used to control the MicrowaveRadar Sensor

__version__ = '0.0.1'
__author__ = 'Nicholas Herriot'
__license__ = "MIT"

# register definitions
OLED_I2C_ADDRESS    = const(0x3c)
OLED_WIDTH          = const(128)                    # Our display is 128 characters wide
OLED_HEIGHT         = const(64)                     # Our display is 64 characters in height

# register Pins for fixed sensors and start time
pir_pin_id = 'X1'                                   # Pin X1 is used to detect events on the PIR controller
mr_pin_id = 'X2'                                    # Pin X2 is used to detect events on the MicrowaveRadar sensor
start_time = time.localtime()                       # Lets store this start time so we know when this particular program has started


# create OLED screen object
i2c = I2C(scl=Pin('X9'), sda=Pin('X10'))            # Create an I2C bus object used to communicate with everything on the I2C bus.
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, OLED_I2C_ADDRESS)      # Create our OLED display object used to output content onto the screen

# create sensor objects


def redraw_screen(name):
    print("Decorator initialised! Name is: ", name)
    def inner_function(func):
        def wrapper(line):
            print("Something is happening before the function is called.")
            print("The clousure parmeter name is: ", name)
            return func(line)
            # print("Something is happening after the function is called.")
        return wrapper
    return inner_function


@redraw_screen(name='Nicholas')
def pir_callback(line):
    # TODO implement a proper logging call to log this event.
    # TODO save this event to a global DB (sqlite and SD card)
    print("=====PIR Callback executed, line number of interrupt is on line: ", line, "=====")






# Create sensor objects


pir = PIR(callback=pir_callback, pir_pin_id='X1')                               # Create our PIR object
mr = MicrowaveRadar(mr_pin_id)                      # Create our MicroWave Radar object

# Callbacks




def microwave_radar_callback():
    # TODO
    pass



# Main Screen
oled.fill(0)
oled.text("Samsung MMS", 0, 0)
connected_info = "WiFi {}".format("Not connected")
oled.text(connected_info, 0, 10)
oled.text("PIR :0 MR :0", 0, 20)
oled.text("Tem :0 deg", 0, 30)
oled.text("Hum :0 %", 0, 40)
oled.text("LUX :0 Lum", 0, 50)
oled.show()


def main_menu(oled_display, pir=0, mr=0, temp=0, humidity=0, lux=0, connected="Not connected"):
    """
        A simple function which will print output to the screen from the sensors used in the demo.
        The function can take 1 mandatory parameter which must be of type SSD1306_I2C from the ssd1306 driver.
        6 optional parameters to be printed on the OLED device, which are defaulted to '0' if not present.
        :param OLED:        Class SSD1306_I2C.
                pir:        integer - representing the number of times this event has happened.
                mr:         integer - represetning the number of times this event has happened.
                temp:       float - representing the temperature recoreded by the temp sensor.
                humidity:   float - the % humidity detected by the humidity sensor.
                lux:        integer - number of lumens detected by the lux sensor.
        :return:
        """

    oled_display.fill(0)
    oled_display.text("Samsung MMS", 0, 0)
    connected_info = "WiFi {}".format(connected)
    oled_display.text(connected_info, 0, 10)
    oled_display.text("PIR: {} MR :{}".format(pir, mr), 0, 20)
    oled_display.text("Tem: {} deg".format(temp), 0, 30)
    oled_display.text("Hum: {} %".format(humidity), 0, 40)
    oled_display.text("LUX: {} Lum".format(lux), 0, 50)
    oled_display.show()


def get_sensor_data(pir, microwave_radar):
    pir_data = pir.pir_total()
    microwave_radar_data = microwave_radar.mr_total()
    pass


def update_screen():
    # TODO
    pass

print('***** Sensor manager active *****')