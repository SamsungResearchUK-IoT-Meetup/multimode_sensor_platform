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

# this key/cert pair is for development only, not to be used in production!
mykey = b'0\x82\x02^\x02\x01\x00\x02\x81\x81\x00\xd9\x1e\x99v6r\ro\xd7\xc2k\x193s\xd9\xf6\xdf28\x01\x14KB$9\x02\xc1\x94\xbb3\x1b\x8c\xc8\x8c85\xbc\xa3G\xa4T~\x8c\'q\xf0\x7f\xf4H\x8dL\x8e\xd82\x8dt\xb3n\xb7\xe1\x9e\x03p\x01\xaey\xe9}\xc9+\x9a{\xe1TM\xb1?1\x18\x10\x97\xfd\x1ciV\x81\x8f\x1c\xab[3\xf2\xc6\xd3\xab\xdf\x9eg\x87\xd80\xf5X]{\x9a\xa0\x89\x05E0V@\xbcn\xfb\xa4\xfb\x083\x1a6\x11i4\x88X\xd3\x02\x03\x01\x00\x01\x02\x81\x80\x0f\r\xd0\x16"0F>:\xf7\x7f\xf5\x7f[\xc9\x01\x14\xf8\xa6il\xbe\xcb\x177\xdc\xb9\x0fV\xebt=\x8e\xaa*;\x8f\x98\xc2\x9e\xe2<\xe3\xfa\xd8+\x94\xb3\x9bT0\xba\xb6\xc2\xca\x8c\x0c\xe4\xe0[\x04Y\xb8\xaaD{\xb5\x0b\x1f\xd11\x90\r\xa5?\xe4\x8e\x0b\x0e\x85\xcb\x18\x18dH g\xe7QB\xb1\xb5d\xbf\xcd\xc3\xa3\xb4\x88\xfe\xb4\xed\x1cfe*\x1e\x7f\xb1\xcb\xe3\xbc\x92\xc3:\x12\xdbQ\xd9\xba\xff\xb7\xf6\x84\xc4F\x10\x01\x02A\x00\xf0H}\xaful)[\xfe\xad"\xbf\xe7\xb0/f\xf4<\xd8\x07\xc70\xba\x1f\xd3\xe3\xed\'*\xb9WX\x88\xb8%AJ\xde\xc1O#dx\xa4|e\xe6\xd8&\xa3\x8bU\xea\n\x96>qiN|\x8c\x96\x03\xe1\x02A\x00\xe7R<\x8c@\x1f\xd0\x9a\x85\x82YC|{\xb1\xa0\xfc5@\xfa\xc5"\xdb\xc3\x89ay\xb8P\xfe>\xb3+\xc2\x80\'=\xc2\xaf2P\x11\xe4\xa2\xb7\x17\xc3\x9b{u\xe9\x9dPN\xce\xfao\xd8 \xda\xeb\xd7\xf33\x02A\x00\xa5\xca.\xc6x\xab\xa7\xa1\xed\x08C\x18\xcc`\xd9d\x1d\x13:/\xab\xb5\xa8F\xbb\xa9\xe1\x81\x0b\xce\x94@\xe7\x1c\xbf\xbf\xdcK\xf4o\x89I\x12\xa0\xd3\xa0o\xf6&:\xe3\xb1\xe4\xe9g\x1f0\x9bkg.\x8dw\xa1\x02A\x00\xacA\xa6\n\xfe\xd9r;\x0f>\xb1\x00;[\xd5;\xbft\\\xae!MB\xff\xcaw\x06\xf0E\x87\xfe\xe2\xe7\xacPHh\x8ahr|\x03\xc7\x11\x90l\xa6\xe2J\xbe\xd4\xb7\xac\x0c\xf3\xbe\xb4\xb8\xeaF|\'\xf4\xd7\x02A\x00\xa1\xc0\xccCx\xee.\x17\xd7w\x02\xc4\x83\x06\xec\x88\xd1c\xa5$\xa0\xbf\x1fl\x99\xde\x19\x88\x888\xca\xe5\xed\xcb\xab-nt\x88\xe6g\x0f\x0eM\xc3\x90\xfa\x90\xa5\xf02\xe3\xf5b\xc47\xec\xe5\x8c\xa8\xadYT\xfb'
mycert = b'0\x82\x02<0\x82\x01\xa5\x02\x02\x03\xe80\r\x06\t*\x86H\x86\xf7\r\x01\x01\x05\x05\x000f1\x0b0\t\x06\x03U\x04\x06\x13\x02UK1\x0f0\r\x06\x03U\x04\x08\x0c\x06London1\x0f0\r\x06\x03U\x04\x07\x0c\x06London1\x100\x0e\x06\x03U\x04\n\x0c\x07Company1\x100\x0e\x06\x03U\x04\x0b\x0c\x07Company1\x110\x0f\x06\x03U\x04\x03\x0c\x08hostname0\x1e\x17\r190927073913Z\x17\r290924073913Z0f1\x0b0\t\x06\x03U\x04\x06\x13\x02UK1\x0f0\r\x06\x03U\x04\x08\x0c\x06London1\x0f0\r\x06\x03U\x04\x07\x0c\x06London1\x100\x0e\x06\x03U\x04\n\x0c\x07Company1\x100\x0e\x06\x03U\x04\x0b\x0c\x07Company1\x110\x0f\x06\x03U\x04\x03\x0c\x08hostname0\x81\x9f0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x81\x8d\x000\x81\x89\x02\x81\x81\x00\xd9\x1e\x99v6r\ro\xd7\xc2k\x193s\xd9\xf6\xdf28\x01\x14KB$9\x02\xc1\x94\xbb3\x1b\x8c\xc8\x8c85\xbc\xa3G\xa4T~\x8c\'q\xf0\x7f\xf4H\x8dL\x8e\xd82\x8dt\xb3n\xb7\xe1\x9e\x03p\x01\xaey\xe9}\xc9+\x9a{\xe1TM\xb1?1\x18\x10\x97\xfd\x1ciV\x81\x8f\x1c\xab[3\xf2\xc6\xd3\xab\xdf\x9eg\x87\xd80\xf5X]{\x9a\xa0\x89\x05E0V@\xbcn\xfb\xa4\xfb\x083\x1a6\x11i4\x88X\xd3\x02\x03\x01\x00\x010\r\x06\t*\x86H\x86\xf7\r\x01\x01\x05\x05\x00\x03\x81\x81\x00\xd0|\xefPO\x8bG7\xbc\xba\xe2\xc5\xeb4S\xa9\xa9l\xe8\xf5\xf8\x1a?u\xcd\x95\x97~\x1e\x9fJ\xfd\x90<\xfb\x16\x96\x8e\xb6h\x8f\xe6,S\xd4\x81\x06\x1aP"\xa9\xa1\t|\xff\x02\x9e\xcec]\xf5{1\xd5\xd0\xf3G\xe5g\x9d\xf4R\x85\xd3D\x11\xa2\xce\xde2\xbe!Mq\xb8e\x19\x08\x1f\xa0\x1e\x98\xf9k\xfd/Y\x8c-\xa11\x12\x01\\\x93e\\\xd0\xe2\xc7\x12\x04\x15\xe8\xf7\x08w\x03h\xde\xc4x\xc2U\xdb0\xab\xa8'

def create_web_server(https=False):
    if https:
        server = MicroWebSrv(webPath='www/', port=8443, sslOptions={'key': mykey, 'cert': mycert})
    else:
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

status = myWifi.connect('Samsung-test', 'test1234')		       # TODO pull the password and SSID from an encrypted file on FLASH

if status[0]:
    print('We have a WiFi connection. Bringing up web server')
    print("\nTo disconnect first import all objects from start.py: '>>> from start import * ' ")
    print("Then to disconnect do: '>>> myWifi.disconnect()' at your repl prompt\n")
    srv= create_web_server()
    print("*** Server now running! ***")





