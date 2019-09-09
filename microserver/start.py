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


__version__ = '0.1.0'
__author__ = 'Nicholas Herriot'
__license__ = "MIT"


from wifi.wifi_connect import *                          # Import the WiFi Manager module to help us monitor and stay connected to poor wifi
from web.microWebSrv import MicroWebSrv                  # Import the WiFi microweb server object to allow us to run a mini web server on the board
from urls import *                                       # Import all the routes that are being used in our web pages and have functions controlling each route
import machine,  ubinascii                               # Used to get machine ID, and convert fro b-strings
#from ssd1306 import SSD1306_I2C

# ============================================================================
# ===( Web Server Process )===================================================
# ============================================================================

srv=None                                                # Make a global variable to hold our server object

def create_web_server():
    server = MicroWebSrv(webPath='www/')
    server.MaxWebSocketRecvLen = 256
    server.WebSocketThreaded = False
    server.AcceptWebSocketCallback = acceptWebSocketCallback
    server.Start(threaded=True)
    return server

# ----------------------------------------------------------------------------


# ============================================================================
# ===( Create WiFi Manager =)=================================================
# ============================================================================

myWifi = Wifi_manager()                                 # Create our WiFi manager object
myWifi.retries(5)                                       # Try connect 5 times since WiFi is so poor


# ============================================================================
# ===( Define URL Path for Status)============================================
# ============================================================================



@MicroWebSrv.route('/status')
def _httpHandlerStatustGet(httpClient, httpResponse):
    content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>Microserver Status</title>
        </head>
        <body>
            <h1>Microserver Status</h1>
            Micorcontroller IP = %s
            <br />
            WiFi SSID = %s
            <br />
            Connection Status = %s
            <br />
            Board Type = %s
            <br />
            Board ID = %s
            <br />
        </body>
    </html>
    """ % (myWifi.status()[1]['Current IP address'],
           myWifi.status()[1]['SSID name'],
           myWifi.status()[1]['Connected'],
           "Micropython:{}".format(srv._boardType),
           ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    httpResponse.WriteResponseOk(headers	= None,
                                  contentType	="text/html", contentCharset="UTF-8",
                                  content 		 =content)


# ============================================================================
# ===( Create A WiFi Connection and Start Web Server )========================
# ============================================================================

status = myWifi.connect('Samsung-test', 'test1234')                  # TODO pull the password and SSID from an encrypted file on FLASH

if status[0]:
    print('We have a WiFi connection. Bringing up web server')
    print("\nTo disconnect first import all objects from start.py: '>>> from start import * ' ")
    print("Then to disconnect do: '>>> myWifi.disconnect()' at your repl prompt\n")
    srv= create_web_server()
    print("*** Server now running! ***")





