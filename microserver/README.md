# Micro Web Server Geting Started
This readme explains how to quickly get up and running your microwebserver on the [Pyboard D](https://pybd.io/) microcontroller.
It uses an excelant open source package from [J-Christophe Bos](https://github.com/jczic) which can be found [here](https://github.com/jczic/MicroWebSrv).

The software is under MIT License. It also incorporates python packages to manage a WiFi connection, PIR sensor and Doppler Radar sensor.
This guide is only about getting the web server running.

## Introduction
The Micro Web Server consists of a root folder and 4 sub directories. The root folder contains the start.py file used to initiate the web server.
There are also the following directories used for:
* **drivers**: Contains python modules to control and use different sensors.
* **web**:     Contains python modules to control and use the microweb server. Taken from https://github.com/jczic/MicroWebSrv
* **wifi**:    Contains python modules to control and monitor your WiFi connection.
* **www**:     Contains all web files for the UI, which contains assets, CSS, Javascript and HTML files.

To get the web server running the following steps need to be done:
1. Update your local copy of start.py with the WiFi SSID and WiFi password of your WiFi network.
2. Copy files accross to the micropython board.
3. From your repl import your start.py file.
Details of how to do this are below:

## 1. Update Start With WiFi Credentials
You will need to update the start.py file with the WiFi SSID and password of your own WiFi network.
In the start.py file at approximately line 101 (*this may be different from the time of writing*) and look for the **connect** method.
You will see a WiFi SSID set as '**test**' and password as '**test1234**'. Change this to your own WiFi credentials.

```python
# ============================================================================
# ===( Create A WiFi Connection and Start Web Server )========================
# ============================================================================

status = myWifi.connect('my-ssid', 'my-wifi-password')                  # TODO pull the password and SSID from an encrypted file on FLASH

if status[0]:
    print('We have a WiFi connection. Bringing up web server')
    print("\nTo disconnect first import all objects from start.py: '>>> from start import * ' ")
    print("Then to disconnect do: '>>> myWifi.disconnect()' at your repl prompt\n")
    srv= create_web_server()
    print("*** Server now running! ***")
```

## 2. Copy Files To Pyboard
From the **microwebserver** directory copy all the files over to your pyboard. You can use your preferred tool for this I've used [rshell](https://github.com/SamsungResearchUK-IoT-Meetup/multimode_sensor_platform/wiki/Micropython-Setup#rshell-environment) to do this.

```bash
   $/multimode_sensor_platform/microserver/>rshell
   Connecting to /dev/ttyACM0 (buffer-size 512)...
   Trying to connect to REPL  connected
   Testing if sys.stdin.buffer exists ... Y
   Retrieving root directories ... /flash/
   Setting time ... Sep 10, 2019 11:38:48
   Evaluating board_name ... pyboard
   Retrieving time epoch ... Jan 01, 2000
   Welcome to rshell. Use Control-D (or the exit command) to exit rshell.
   cp -r * /flash/
```

This could take 30 seconds or so...

## 3. From REPL Import Start To Start Web Server
The Microweb server should be ready to go. From your command line start the REPL:

```bash
   /> repl
   $Entering REPL. Use Control-X to exit.
   >
   MicroPython v1.11-63-gd889def-dirty on 2019-07-02; PYBD-SF2W with STM32F722IEK
   Type "help()" for more information.
   >>> 
   >>>
```

To start the web server import the start python file:

```bash
   >>> import start
   WiFi Manager bringing up wlan interface.
   Trying to connect to SSID: srbackup
   Retrying to connect. Trying 0 of 5's
   Retrying to connect. Trying 1 of 5's
   WiFi Manager is now monitoring the connection
   We have a WiFi connection. Bringing up web server

   To disconnect first import all objects from start.py: '>>> from start import * ' 
   Then to disconnect do: '>>> myWifi.disconnect()' at your repl prompt

   *** Server now running! ***
```
You will notice that every 10 seconds the WiFi manager will output the connected IP address as it tests the connection. 
Use this to check status of the web server:

```bash
*** Server now running! ***
>>> Connected on IP: 192.168.110.227
Connected on IP: 192.168.110.227
Connected on IP: 192.168.110.227
```
On your browser go to the IP address: http://192.168.110.227:8000/status
You should see output similar to the following on your browser:

![status page sceen shot](https://github.com/SamsungResearchUK-IoT-Meetup/multimode_sensor_platform/blob/master/assets/screenshots/microwebServeStatusPage.png)


