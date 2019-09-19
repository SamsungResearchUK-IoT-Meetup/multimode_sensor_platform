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


import machine, pyb, time

__version__ = '0.1.0'
__author__ = 'Nicholas Herriot'
__license__ = "MIT"


class OPT_Sensor:
    """
    A pythonic OPT (Lux sensor OPT3001) driver for micropython

    This is based on the OPT3001 class defined at Micropython here: https://pybd.io/hw/tile_sensa.html#opt-lux-sensor

    The driver knows how to talk I2C to the tile OPT3001 sensor on the board. It uses the I2C address and register values to fetch LUX
    data from the tile. Every time the object reads a value it checks to see if this is the highest or lowest value, if it is
    it records this for max/min values.
    At the time of writing none of the other methods have been written yet.

    The OPT object has internal state for:
     - number of activations since it was active.
     - the time stamp in UCT time when the object was created.
     - a method to GET the current LUX level of sensor.
     - a method to GET maximum LUX level recorded by the OPT sensor object (not the maximum of the sensor)
     - a method to GET minimum LUC level recorded by the OPT sensor object (not the minimum of the sensor)
     - TODO a method to start polling the LUX sensor to record on SD card
     - TODO a method to set polling in seconds between 1 and 10 seconds.
     - TODO a method to stop polling the LUX sensor.
     - TODO a method to fetch all LUX readings in  a JSON format.
     - TODO bring logging into this module.


    References:
    * https://pybd.io/hw/tile_sensa.html#opt-lux-sensor
    * https://i2c.info/

    """

    def __init__(self, i2c_peripheral, i2c_addr=69):
        self.i2c_peripheral = i2c_peripheral
        self.i2c_addr = i2c_addr
        self._max_lux = 0
        self._min_lux = 0
        self.start_time = time.time()
        self._polling_period = 10
        self._register_address_set = 0x01
        self._register_address_lux = 0
        self._register_address_humidity = 0x02
        self._read_bytes = 2

    @staticmethod
    def convert_lux(opt_lux):
        lux_level = 0.01 * 2 ** (opt_lux[0] >> 4) * ((opt_lux[0] & 0x0f) << 8 | opt_lux[1])

        return lux_level

    def is_ready(self):
        try:
            if (self.i2c_peripheral.readfrom_mem(self.i2c_addr, self._register_address_set, 2)[1] & 0x10) :
                return True
            else:
                return False
        except OSError as error:
            print("The I2C bus is not responding to the I2C device address of: {}".format(self.i2c_addr))
            print("Error value: {}".format(error))
        except:
            # TODO put logging into this
            print("An unexpected error occurred while attempting to read a temperature value")
            raise
        return False

    def _measure(self):
        """
        Make the sensor read a new set of values into the temperature and humidity registers of the I2C sensor.
        :return:
        """
        self.i2c_peripheral.writeto_mem(self.i2c_addr, self._register_address_set, b'\xca\x10')

    def max_lux(self):
        return self._max_lux

    def min_lux(self):
        return self._min_lux

    def lux(self):
        """
        Returns the lux level from the I2C sensor

        :return: float
        """
        try:
            self._measure()
            data = self.i2c_peripheral.readfrom_mem(self.i2c_addr, self._register_address_lux, self._read_bytes)
            lux_level = self.convert_lux(data)
            if lux_level > self._max_lux:
                self._max_lux = lux_level
            if lux_level < self._min_lux:
                self._min_lux = lux_level
        except OSError as error:
            print("The I2C bus is not responding to the I2C device address of: {}".format(self.i2c_addr))
            print("Error value: {}".format(error))
            lux_level = 0
        except:
            # TODO put logging into this
            print("An unexpected error occurred while attempting to read a temperature value")
            raise
        return lux_level


    def polling(self, polling_period=None):
        """
         The polling is used to control how many times per second the hdc sensor will attempt to read a value for lux.
         It returns True if the user passes a value between 1 and 10 or False with an error message if it is not in that range.
         It returns the current setting in second if no value is given.

         :return (boolean,  string) OR int:
         """
        if polling_period is None:
            return self._polling_period
        return_value = True
        message = None

        try:
            self._polling_period = 0
            self._polling_period += polling_period
            if isinstance(self._polling_period, float):
                self._polling_period = int(self._polling_period)
            if (self._polling_period >10) | (self._polling_period <1):
                raise TypeError
        except TypeError as error:
            return_value = False
            message = "You must input an integer value between 1 and 10 to set the polling period"
            self._polling_period = 10  # Reset the retires count back to default TODO make this a config paramter.
        except:
            # TODO put logging into this
            print("Unexpected error!")
            raise

        return return_value, message
