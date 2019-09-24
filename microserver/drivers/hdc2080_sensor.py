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


class HDC_Sensor:
    """
    A pythonic HDC (Temperature and Humidity sensor HDC280) driver for micropython

    This is based on the HDC2080 class defined at Micropython here: https://pybd.io/hw/tile_sensa.html#hdc-temperature-and-humidity-sensor

    The driver knows how to talk I2C to the tile HDC sensor on the board. It uses the I2C address and register values to fetch humidity and
    temperature data from the tile. Every time the object reads a value it checks to see if this is the highest or lowest value, if it is
    it records this for max/min values.
    At the time of writing none of the other methods have been written yet.

    The HDC object has internal state for:
     - number of activations since it was active.
     - the time stamp in UCT time when the object was created.
     - a method to GET the current temperature of sensor.
     - a method to GET the humidity of the sensor.
     - a method to GET maximum temperature recorded by the HDC sensor object (not the maximum of the sensor)
     - a method to GET minimum temperature recorded by the HDC sensor object (not the minimum of the sensor)
     - TODO a method to start polling the temperature sensor to record on SD card
     - TODO a method to start polling the humidity sensor to record to SD card
     - TODO a method to set polling in seconds between 1 and 10 seconds.
     - TODO a method to stop polling humidity sensor.
     - TODO a method to stop polling temperature sensor.
     - TODO a method to fetch all temperature readings in  a JSON format.
     - TODO a method to fetch all humidity readings in a JSON format.
     - TODO bring logging into this module.


    References:
    * https://pybd.io/hw/tile_sensa.html#hdc-temperature-and-humidity-sensor
    * https://i2c.info/

    """

    def __init__(self, i2c_peripheral, i2c_addr=64):
        self.i2c_peripheral = i2c_peripheral
        self.i2c_addr = i2c_addr
        self._max_temp = 0
        self._min_temp = 0
        self.start_time = time.time()
        self._polling_period = 10
        self._register_address_set = 0x0f
        self._register_address_temp = 0x00
        self._register_address_humidity = 0x02
        self._read_bytes = 2

    @staticmethod
    def convert_hdc_temp(hdc_temp):
        temp_in_degrees = hdc_temp / 0x10000 * 165 - 40

        return temp_in_degrees

    @staticmethod
    def convert_hdc_humidity(hdc_humidity):
        humidity_percentage = hdc_humidity / 0x10000 * 100

        return humidity_percentage

    def is_ready(self):
        try:
            if not (self.i2c_peripheral.readfrom_mem(self.i2c_addr, self._register_address_set, 1)[0]):
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
        self.i2c_peripheral.writeto_mem(self.i2c_addr, self._register_address_set, b'\x01')

    def max_temperature(self):
        return self._max_temp

    def min_temperature(self):
        return self._min_temp

    def temperature(self):
        """
        Returns the temperature in degrees centigrade from the I2C sensor

        :return: float
        """
        try:
            self._measure()
            data = self.i2c_peripheral.readfrom_mem(self.i2c_addr, self._register_address_temp, self._read_bytes)
            data = data[0] | data[1] << 8
            temp_in_degrees = self.convert_hdc_temp(data)
            if temp_in_degrees > self._max_temp:
                self._max_temp = temp_in_degrees
            if temp_in_degrees < self._min_temp:
                self._min_temp = temp_in_degrees
        except OSError as error:
            print("The I2C bus is not responding to the I2C device address of: {}".format(self.i2c_addr))
            print("Error value: {}".format(error))
            temp_in_degrees = 0
        except:
            # TODO put logging into this
            print("An unexpected error occurred while attempting to read a temperature value")
            raise
        return temp_in_degrees



    def humidity(self):
        """
        Returns the humidity in percentage humidity from the I2C sensor

        :return: flaot
        """
        try:
            self._measure()
            data = self.i2c_peripheral.readfrom_mem(self.i2c_addr, self._register_address_humidity, self._read_bytes)
            data = data[0] | data[1] << 8
            humidity_in_percentage = self.convert_hdc_humidity(data)
        except OSError as error:
            print("The I2C bus is not responding to the I2C device address of: {}".format(self.i2c_addr))
            print("Error value: {}".format(error))
            humidity_in_percentage = 0
        except:
            # TODO put logging into this
            print("An unexpected error occurred while attempting to read a temperature value")
            raise
        return humidity_in_percentage

    def polling(self, polling_period=None):
        """
         The polling is used to control how many times per second the hdc sensor will attempt to read a value for temp and
         humidity.
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
