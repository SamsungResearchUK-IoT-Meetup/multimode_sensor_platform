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

from web.microWebSrv import MicroWebSrv                # Import the WiFi microweb server object to allow us to run a mini web server on the board
from drivers.sr_501_sensor import PIR
from  drivers.rcwl_0516_sensor import MicrowaveRadar
# ----------------------------------------------------------------------------





# ============================================================================
# ================( Create Sensor Objects)====================================
# ============================================================================

p1 = PIR(pir_pin_id='X1')                   # Create Sensor which uses the 'X1' pin to detect movement
p1.start()                                  # Start the PIR sensor

mr1 = MicrowaveRadar(mr_pin_id='X2')        # Create Sensor which uses the 'X1' pin to detect movement
mr1.start()                                 # Start the PIR sensor


# ============================================================================
# ===( Define URL Path for pages)=============================================
# ============================================================================

@MicroWebSrv.route('/test')
def _httpHandlerTestGet(httpClient, httpResponse):
    content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
			<form action="/test" method="post" accept-charset="ISO-8859-1">
				First name: <input type="text" name="firstname"><br />
				Last name: <input type="text" name="lastname"><br />
				<input type="submit" value="Submit">
			</form>
        </body>
    </html>
	""" % httpClient.GetIPAddr()
    httpResponse.WriteResponseOk(headers	= None,
                                  contentType	= "text/html",contentCharset = "UTF-8",
                                  content 		 = content)




@MicroWebSrv.route('/sensors')
def _httpHandlerTestGet(httpClient, httpResponse):
    content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>Sensors Page</title>
        </head>
        <body>
            <h1>Sensors Page</h1>
            PIR Sensor:  %s
            <br />
            Doppler Radar: %s
            <br />
            Temperature Sensor: %s
            <br />
            LUX Light Level: %s
            <br />
            Humidity Level: %s
            <br />
            LED Light: %s
            <br />
        </body>
    </html>
	""" % (p1.pir_total(), mr1.mr_total(), "N/A", "N/A", "N/A", "N/A",)
    httpResponse.WriteResponseOk(headers	= None,
                                  contentType	= "text/html",contentCharset = "UTF-8",
                                  content 		 = content)




@MicroWebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient,httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname = formData["lastname"]
    content = """\
	<!DOCTYPE html>
	<html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
	""" % (MicroWebSrv.HTMLEscape(firstname),
           MicroWebSrv.HTMLEscape(lastname))
    httpResponse.WriteResponseOk(headers	= None,
                                  contentType	= "text/html",contentCharset = "UTF-8",
                                  content 		 = content)


@MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}):
    content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
    content += "<h1>EDIT item with {} variable arguments</h1>".format(len(args))

    if 'index' in args :
        content += "<p>index = {}</p>".format(args['index'])

    if 'foo' in args :
        content += "<p>foo = {}</p>".format(args['foo'])

    content += """
        </body>
    </html>
	"""
    httpResponse.WriteResponseOk(headers = None,contentType	 = "text/html",
                                  contentCharset = "UTF-8",
                                  content = content)
# ----------------------------------------------------------------------------


def acceptWebSocketCallback(webSocket, httpClient) :
    print("WS ACCEPT")
    webSocket. RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket. ClosedCallback = _closedCallback


def recvTextCallback(webSocket, msg):
    print("WS RECV TEXT : %s" % msg)
    webSocket.SendText("Reply for %s" % msg)


def recvBinaryCallback(webSocket, data):
    print("WS RECV DATA : %s" % data)


def closedCallback(webSocket):
    print("WS CLOSED")

# ----------------------------------------------------------------------------

# Create a list of tuples which hold the URL path being mapped to via HTTP methods POS,PUT,GET, DELETE. And mapes a handler for that tuple.
#routeHandlers = [
#	( "/test",	"GET",	_httpHandlerTestGet ),
#	( "/test",	"POST",	_httpHandlerTestPost )
#]
