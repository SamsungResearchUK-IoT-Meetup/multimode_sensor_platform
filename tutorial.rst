Introduction to the pyboard D
=============================

Welcome to the MicroPython pyboard D tutorial.
To get the most out of your pyboard, there are a few basic things to
understand about how it works.

Caring for your pyboard
-----------------------

Because the pyboard does not have a housing it needs a bit of care:

  - Be gentle when plugging/unplugging the USB cable.  Whilst the USB connector
    is soldered through the board and is relatively strong, if it breaks off
    it can be very difficult to fix.

  - Static electricity can shock the components on the pyboard and destroy them.
    If you experience a lot of static electricity in your area (eg dry and cold
    climates), take extra care not to shock the pyboard.  If your pyboard came
    in a black plastic box, then this box is the best way to store and carry the
    pyboard as it is an anti-static box (it is made of a conductive plastic, with
    conductive foam inside).

As long as you take care of the hardware, you should be okay.  It's almost
impossible to break the software on the pyboard, so feel free to play around
with writing code as much as you like.  If the filesystem gets corrupt, see
below on how to reset it.  In the worst case you might need to reflash the
MicroPython software, but that can be done over USB.

To start with the Mulit-mode Sensor project this hardware is required:

HARDWARE
--------

  - MicroPython pyboard D SF2-W4F2 (will work with SF3 and SF6 as well) `PYBD-SF2-W4F2 <https://store.micropython.org/product/PYBD-SF2-W4F2>`_
  - MicroPython adapter WBUS-DIP68 for connecting external sensors `WBUS-DIP68 <https://store.micropython.org/product/WBUS-DIP68>`_
  - MicroPython SensorTile with temperature, humidity, light and RGB-LED `TILE-SENSA <https://store.micropython.org/product/TILE-SENSA>`_
  - Micro-USB to USB cable for connecting your pyboard to your machine
  
SOFTWARE
--------

  - This project requires at least firmware version v1.10 with the threading enabled. First make sure which firmware version runs on your pyboard D.
  To do this, you can type this command into the repl:
  
  .. code-block:: python

    import os
    os.uname()
    
The version will tell you which firmware is currently running on the pyboard.
If the firmware which runs on the pybaord doesn't support threating yet, you can download this firmware image:: and install it onto your
pyboard following these instructions: `Firmware-upgrade <https://github.com/micropython/micropython/wiki/Pyboard-Firmware-Update>`_
    
The MicroPython pyboard D doesn't need to be put manually into the dfu mode for upgrading the firmware.
Simply type pyb.bootloader() into the comand line of your console and follwing the steps mentioned bellow.

  .. code-block:: python
  
    pyb.bootloader()

Your pyboard D is in dfu-mode, when you see the RGB-LED flashing red every second.

To get you up and running with the Mulitmode sensor platform, firstly one needs to set-up the MicroWebserver link::
You can put the software onto your pyboard D with simply copying the file:: to your 'PYBFLASH'

Now you have to make sure to run the 
