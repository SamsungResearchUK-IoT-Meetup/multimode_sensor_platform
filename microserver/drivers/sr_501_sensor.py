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


import pyb, time

__version__ = '0.1.0'
__author__ = 'Nicholas Herriot'
__license__ = "MIT"


def simple_test_callback(line):
    """
    A simple test callback you can use to pass into the PIR object when you instantiate
    the PIR class.
    The callback function will print the time it was called and the line number parameter.
    :param line: A string which contains the pin number that was triggered on the interrupt signal.
    :return:
    """
    print("*** Test callback function ***\n")
    print("    Line value is:   ", line, "\n    Program Time is: ", time.time())


class PIR:
    """
    A pythonic PIR (Passive Infrared Sensor for the SR-501) driver for micropython

    The driver sets an interrupt for the PIR sensor when initialised. The constructor will try and use pin X1 if it is not
    instantiated with a Pin value. If an interrupt is already being used on that Pin the object will raise an exception. In
    this instance the application layer has to deal with this.
    Once the object is created it will call the 'callback' function passed in when being created. If none is given a default
    callback is used which simply outputs text to the screen.

    The PIR object has internal state for:
     - number of activations since it was active.
     - the time stamp in UCT time when the object was created.
     - a method to deactivate the interrupt on the pin
     - a method to get stats from the PIR object
     - a method to start the interrupt on the given pin.
     - a method to manually pole the PIR to see if it is active or not.

    References:
    * http://www.instructables.com/id/PIR-Motion-Sensor-Tutorial/?ALLSTEPS
    * http://www.datasheet-pdf.info/entry/HC-SR501-Datasheet-PDF
    * https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor/overview
    * https://github.com/SamsungResearchUK-IoT-Meetup/projects/wiki/Sensors
    """

    def __init__(self, callback=simple_test_callback, pir_pin_id='X1'):
        self.callback = callback
        self.pir_pin = pir_pin_id
        self._pir_pin_object = pyb.Pin(pir_pin_id, pyb.Pin.IN)
        self.start_time = time.time()
        self._active = False
        self._callback_on = True
        self._last_detection = None
        self._number_of_triggers = 0
        self._pir_interrupt = None

    def pir_callback(self, line_number):
        print("PIR callback called with line number: ", line_number)
        self._number_of_triggers += 1               # count the number of times we get a pulse
        self._last_detection = time.time()          # record the last time we got a trigger
        self._active = True
        if self._callback_on:
            self.callback(line_number)
        else:
            print("Interrupt on Pin: ", self.pir_pin, " detected")

    def start(self):
        """
        Try and create an external interrupt for the supplied Pin. If successful your 'callback' will be called every time the PIR
        sensor detects a movement.
        :return: bool, error_message
        """
        return_value = True
        error_message = None
        try:
            self._pir_interrupt = pyb.ExtInt('X1', pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, self.pir_callback)
        except ValueError as error:
            print(error.args[0])
            if error.args[0] == "ExtInt vector {0} is already in use".format(self._pir_interrupt.line()):
                self._pir_interrupt.enable()
                return return_value, "PIR is now enabled"
            else:
                print("ValueError: {0}".format(error))
                return_value = False
                error_message = error

        except OSError as error:
            print("OS Error: {0}".format(error))
            return_value = False
            error_message = error

        except:
            print("Unexpected error!")
            raise

        return return_value, error_message

    def stop(self):
        """
        Stops the external interrupt for the supplied Pin. If successful will return 'OK'. The method will handle if it's called
        without first being started.
        sensor detects a movement.
        :return: bool, error_message
        """

        if self._pir_interrupt == None:
            message = "You need to first start the pir with the start method before stopping it. e.g. 'MyPIR.start()' "
            return False, message
        try:
            self._pir_interrupt.disable()
        except OSError as error:
            print("OS Error: {0}".format(error))
            return False, error
        except:
            print("Unexpected error!")
            raise
        self._active = False
        return True, "OK"

    def reset(self, ):
        # TODO reset the active flag, the number of PIR triggers detected and the time.
        # TODO We should make this accept a paramter to reset any one of the given variables
        pass

    def clear(self):
        """
        Remove all registered callback methods
        """
        self._callback_on = None

    def update(self, callback):
        # TODO update the callback that was registered with the interrupt with a new callback
        pass

    def pir_total(self):
        """
        Return the total number of times the PIR has been activated since it has been switched on
        :return: number_of_triggers
        """
        return self._number_of_triggers

    def pir_stats(self):
        """
        Returns a dictionary with the number of trigger events, program start time with reference to when the
        microcontroller started, and the last trigger event.
        :return: dictionary {
                        "trigger events": int
                        "start time": UCT time
                        "last trigger event": UCT time
        """
        stats = {"Trigger Events": self._number_of_triggers,
                 "Start Time": self.start_time,
                 "Last Event": self._last_detection}

        return stats

    def is_active(self):
        """
        Return true if the sensor has been activated since it's been switched on.
        :return: bool
        """
        return self._active

    def is_currently_active(self):
        """
        Return true if the sensor is currently detecting movement. This polls the Pin to see if it's
        high = active or low = inactive
        :return: value 0 or 1
        """
        return self._pir_pin_object.value()
