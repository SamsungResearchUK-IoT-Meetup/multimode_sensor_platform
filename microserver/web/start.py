

from microWebSrv import MicroWebSrv                  # Import the WiFi microweb server object to allow us to run a mini web server on the board

# ============================================================================
# ===( Web Server Process )===================================================
# ============================================================================

srv=None                                                # Make a global variable to hold our server object


def acceptWebSocketCallback(webSocket, httpClient) :
    print("WS ACCEPT")
    webSocket. RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket. ClosedCallback = _closedCallback



def create_web_server():
    server = MicroWebSrv(webPath='www/')
    server. MaxWebSocketRecvLen = 256
    server.WebSocketThreaded = False
    server.AcceptWebSocketCallback = acceptWebSocketCallback
    server.Start(threaded=True)
    return server

# ----------------------------------------------------------------------------

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
    """ % ('Current IP address',
           'SSID name',
           'Connected',
           "Micropython",
           ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    httpResponse.WriteResponseOk(headers	= None,
                                  contentType	="text/html", contentCharset="UTF-8",
                                  content 		 =content)

# ============================================================================
# ===( Create A WiFi Connection and Start Web Server )========================
# ============================================================================

status = [True]

if status[0]:
    print('We have a WiFi connection. Bringing up web server')
    print("\nTo disconnect first import all objects from start.py: '>>> from start import * ' ")
    print("Then to disconnect do: '>>> myWifi.disconnect()' at your repl prompt\n")
    srv= create_web_server()
    print("*** Server now running! ***")





