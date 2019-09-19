"""
The MIT License (MIT)
Copyright © 2018 Jean-Christophe Bos & HC² (www.hc2.fr)
"""


from    json        import loads, dumps
from    os          import stat, uname
from    _thread     import start_new_thread
import  socket
import  gc
import  re

from libraries.logging.logging import *

basicConfig(level=DEBUG)                 # Can be one of NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
log = getLogger("microWebSrv")

# try:
#     1/0
# except Exception as e:
#     log.exc(e, "Problem with 1/0. Expected: (%s)", "infinity")

try :
    from microWebTemplate import MicroWebTemplate
except :
    pass

try :
    from microWebSocket import MicroWebSocket
except :
    pass

class MicroWebSrvRoute :
    def __init__(self, route, method, func, routeArgNames, routeRegex) :
        self.route         = route        
        self.method        = method       
        self.func          = func         
        self.routeArgNames = routeArgNames
        self.routeRegex    = routeRegex   


class MicroWebSrv :

    # ============================================================================
    # ===( Constants )============================================================
    # ============================================================================

    _indexPages = [
        "index.pyhtml",
        "index.html",
        "index.htm",
        "default.pyhtml",
        "default.html",
        "default.htm"
    ]

    _mimeTypes = {
        ".txt"   : "text/plain",
        ".htm"   : "text/html",
        ".html"  : "text/html",
        ".css"   : "text/css",
        ".csv"   : "text/csv",
        ".js"    : "application/javascript",
        ".xml"   : "application/xml",
        ".xhtml" : "application/xhtml+xml",
        ".json"  : "application/json",
        ".zip"   : "application/zip",
        ".pdf"   : "application/pdf",
        ".jpg"   : "image/jpeg",
        ".jpeg"  : "image/jpeg",
        ".png"   : "image/png",
        ".gif"   : "image/gif",
        ".svg"   : "image/svg+xml",
        ".ico"   : "image/x-icon"
    }

    _html_escape_chars = {
        "&" : "&amp;",
        '"' : "&quot;",
        "'" : "&apos;",
        ">" : "&gt;",
        "<" : "&lt;"
    }

    _pyhtmlPagesExt = '.pyhtml'

    # ============================================================================
    # ===( Class globals  )=======================================================
    # ============================================================================

    _docoratedRouteHandlers = []

    # ============================================================================
    # ===( Utils  )===============================================================
    # ============================================================================

    @classmethod
    def route(cls, url, method='GET'):
        """Adds a route handler function to the routing list. """
        def route_decorator(func):
            item = (url, method, func)
            cls._docoratedRouteHandlers.append(item)
            return func
        return route_decorator

    # ----------------------------------------------------------------------------

    @staticmethod
    def HTMLEscape(s) :
        """Removes characters that are parsed as HTML and replaces them with HTML control characters.

        For example the string: '<p>hello world</p>' gets changed to: '&lt;p&gt;hello world&lt;/p&gt;'
        It's used to clean text strings that can be passed into HTML forms."""
        return ''.join(MicroWebSrv._html_escape_chars.get(c, c) for c in s)

    # ----------------------------------------------------------------------------

    @staticmethod
    def _startThread(func, args=()):
        log.debug("New thread started for Function: %s and with arguments: %s", func, args)
        try :
            start_new_thread(func, args)
        except :
            global _mwsrv_thread_id
            try :
                _mwsrv_thread_id += 1
            except :
                _mwsrv_thread_id = 0
            try :
                start_new_thread('MWSRV_THREAD_%s' % _mwsrv_thread_id, func, args)
            except :
                return False
        return True

    # ----------------------------------------------------------------------------

    @staticmethod
    def _unquote(s) :
        r = s.split('%')
        for i in range(1, len(r)):
            s = r[i]
            try :
                r[i] = chr(int(s[:2], 16)) + s[2:]
            except :
                r[i] = '%' + s
        return ''.join(r)

    # ------------------------------------------------------------------------------

    @staticmethod
    def _unquote_plus(s):
        return MicroWebSrv._unquote(s.replace('+', ' '))

    # ------------------------------------------------------------------------------

    @staticmethod
    def _fileExists(path):
        """A private helper method to find out if a directory path exists.
        It returns 'True' if the directory exists in the current path.
        It returns 'False' if the directory does not exist in the current path.

        :param path:
        :return: Boolean
        Example: If the directory '/www' exists then:
            myWebSrv._fileExists("www") Returns: 'True'
            myWebSrv._fileExists("WWW") Returns: 'True'
            myWebSrv._fileExists("nothing_here") Returns: 'False'.
        """
        try :
            stat(path)
            return True
        except :
            return False

    # ----------------------------------------------------------------------------

    @staticmethod
    def _isPyHTMLFile(filename):
        """
        A simple helper method which returns true if a file name ends in 'pyhtml'.
        :param filename:
        :return: Boolean

        Example: myServer._isPyHTMLFile('myFileName.pyhtml') Returns: 'True'
        """
        return filename.lower().endswith(MicroWebSrv._pyhtmlPagesExt)

    # ============================================================================
    # ===( Constructor )==========================================================
    # ============================================================================

    def __init__( self,
                  routeHandlers = [],
                  port          = 8000,
                  bindIP        = '0.0.0.0',
                  webPath       = "/flash/www" ) :

        self._srvAddr       = (bindIP, port)
        self._webPath       = webPath
        self._notFoundUrl   = None
        self._started       = False

        self.MaxWebSocketRecvLen        = 1024
        self.WebSocketThreaded          = True
        self.AcceptWebSocketCallback    = None
        self.LetCacheStaticContentLevel = 2

        self._routeHandlers = []
        routeHandlers += self._docoratedRouteHandlers
        for route, method, func in routeHandlers :
            routeParts = route.split('/')
            # -> ['', 'users', '<uID>', 'addresses', '<addrID>', 'test', '<anotherID>']
            routeArgNames = []
            routeRegex    = ''
            for s in routeParts :
                if s.startswith('<') and s.endswith('>') :
                    routeArgNames.append(s[1:-1])
                    routeRegex += '/(\\w*)'
                elif s :
                    routeRegex += '/' + s
            routeRegex += '$'
            # -> '/users/(\w*)/addresses/(\w*)/test/(\w*)$'
            routeRegex = re.compile(routeRegex)

            self._routeHandlers.append(MicroWebSrvRoute(route, method, func, routeArgNames, routeRegex))

        self._boardType = uname()[4].split()[0]      # Provides the name of the actual board being used

    # ============================================================================
    # ===( Server Process )=======================================================
    # ============================================================================

    def _serverProcess(self):
        self._started = True
        log.debug("Server Process is now started. About to accept SOCKET incoming connections")
        while True :
            try :
                client, cliAddr = self._server.accept()         # Blocking on socket.accept()
                log.info("Accepted 'client': %s and 'client address': %s", client, cliAddr)
            except Exception as ex :
                if ex.args and ex.args[0] == 113 :
                    break
                continue
            self._client(self, client, cliAddr)                 # Calling _client to process request.
        self._started = False

    # ============================================================================
    # ===( Functions )============================================================
    # ============================================================================

    def Start(self, threaded=False):
        """
        The main method to start the web server. Takes a single parameter 'threaded' which is defaulted to 'False'.
        If threaded is false the method will use the private _serverProcess which is an endless while loop blocking on
        the socket.accept() method.
        If threaded is true the method will pass the private -serverProcess into the _startThread process to use the
        threading module. This allows the use of the repl when running the server.

        :param threaded:
        :return:
        """
        if not self._started :
            self._server = socket.socket()
            self._server.setsockopt( socket.SOL_SOCKET,
                                     socket.SO_REUSEADDR,
                                     1 )
            self._server.bind(self._srvAddr)
            self._server.listen(1)
            if threaded :
                MicroWebSrv._startThread(self._serverProcess)
            else :
                self._serverProcess()

    # ----------------------------------------------------------------------------

    def Stop(self):
        if self._started:
            self._server.close()

    # ----------------------------------------------------------------------------

    def IsStarted(self):
        return self._started

    # ----------------------------------------------------------------------------

    def SetNotFoundPageUrl(self, url=None):
        self._notFoundUrl = url

    # ----------------------------------------------------------------------------

    def GetMimeTypeFromFilename(self, filename):
        """
        Searches self._mimeTypes to verify that this mimeType is supported. If this mime type is supported the method responds with
        the mime type e.g. 'text'.
        If it's not supported 'None' is returned.

        :param filename:
        :return: mimeType | None
        """
        filename = filename.lower()
        for ext in self._mimeTypes :
            if filename.endswith(ext) :
                return self._mimeTypes[ext]
        return None

    # ----------------------------------------------------------------------------
    
    def GetRouteHandler(self, resUrl, method):
        """
        The method will take a HTTP method(POST,PUT, DELETE, GET) and URL path. It removes '/' at the end of a URL path. It then iterates around
        the routehandlers that are configured upon creation (e.g. /test, /status, /myPath etc..) and checks to see if there is a handler for the
        given resUrl.
        If there is a match, the function that is attached to that route (e.g. path=/mypath: func=myURLfunction) will be passed back to the caller.
        This is used

        :param resUrl:
        :param method:
        :return: route handler function && args | None && None
        """
        if self._routeHandlers :
            #resUrl = resUrl.upper()
            if resUrl.endswith('/') :
                resUrl = resUrl[:-1]
            method = method.upper()
            for rh in self._routeHandlers :
                if rh.method == method :
                    m = rh.routeRegex.match(resUrl)
                    if m :   # found matching route?
                        if rh.routeArgNames :
                            routeArgs = {}
                            for i, name in enumerate(rh.routeArgNames) :
                                value = m.group(i+1)
                                try :
                                    value = int(value)
                                except :
                                    pass
                                routeArgs[name] = value
                            return (rh.func, routeArgs)
                        else :
                            return (rh.func, None)
        return (None, None)

    # ----------------------------------------------------------------------------

    def _physPathFromURLPath(self, urlPath):
        """
        A private helper method to translate a URL path for a file resource to a physical path on the device.
        If a request is made for www.server.com/ i.e. default page which normally serves up index.html the method will search
        self._indexPages on your embedded system, and if the first file that exists will be returned as the physical file to serve.
        If it is for an actual file e.g. www.server.com/my.pdf then the path is returned if the file exists on the server.
        If no file exists then 'None' is returned

        :param urlPath:
        :return: None | pysPath
        """
        if urlPath == '/' :
            for idxPage in self._indexPages :
            	physPath = self._webPath + '/' + idxPage
            	if MicroWebSrv._fileExists(physPath) :
            		return physPath
        else :
            physPath = self._webPath + urlPath
            if MicroWebSrv._fileExists(physPath) :
                return physPath
        return None

    # ============================================================================
    # ===( Class Client  )========================================================
    # ============================================================================

    class _client :
        """
        The main embedded class that handles requests from a client (browser).

        """

        # ------------------------------------------------------------------------

        def __init__(self, microWebSrv, socket, addr):
            socket.settimeout(4)
            self._microWebSrv   = microWebSrv
            self._socket        = socket
            self._addr          = addr
            self._method        = None
            self._path          = None
            self._httpVer       = None
            self._resPath       = "/"
            self._queryString   = ""
            self._queryParams   = { }
            self._headers       = { }
            self._contentType   = None
            self._contentLength = 0
            
            if hasattr(socket, 'readline'):   # MicroPython
                self._socketfile = self._socket
            else:   # CPython
                self._socketfile = self._socket.makefile('rwb')
                        
            self._processRequest()

        # ------------------------------------------------------------------------

        def _processRequest(self):
            """
            This private method of embedded class '_client' is responsible for processing HTTP requests from the client.

            :return:
            """
            try :
                response = MicroWebSrv._response(self)              # create a response object template which is empty at this point.
                if self._parseFirstLine(response) :
                    if self._parseHeader(response) :
                        upg = self._getConnUpgrade()                # check to see if we can upgrade to web sockets.
                        if not upg :
                            routeHandler, routeArgs = self._microWebSrv.GetRouteHandler(self._resPath, self._method)
                            if routeHandler :                       # If we have a route handler function for this URL patth then use it to handle the response.
                                if routeArgs is not None:
                                    routeHandler(self, response, routeArgs)
                                else:
                                    routeHandler(self, response)
                            elif self._method.upper() == "GET" :    # We only allow default GET requests to the server if not handled explicitly
                                filepath = self._microWebSrv._physPathFromURLPath(self._resPath)        # Get a file path if it is valid and exists
                                if filepath :
                                    if MicroWebSrv._isPyHTMLFile(filepath) :
                                        response.WriteResponsePyHTMLFile(filepath)
                                    else :
                                        contentType = self._microWebSrv.GetMimeTypeFromFilename(filepath)
                                        if contentType :
                                            if self._microWebSrv.LetCacheStaticContentLevel > 0 :
                                                if self._microWebSrv.LetCacheStaticContentLevel > 1 and \
                                                   'if-modified-since' in self._headers :
                                                    response.WriteResponseNotModified()
                                                else:
                                                    headers = { 'Last-Modified' : 'Fri, 1 Jan 2018 23:42:00 GMT', \
                                                                'Cache-Control' : 'max-age=315360000' }
                                                    response.WriteResponseFile(filepath, contentType, headers)
                                            else :
                                                response.WriteResponseFile(filepath, contentType)
                                        else :
                                            response.WriteResponseForbidden()
                                else :
                                    response.WriteResponseNotFound()
                            else :
                                response.WriteResponseMethodNotAllowed()
                        elif upg == 'websocket' and 'MicroWebSocket' in globals() \
                             and self._microWebSrv.AcceptWebSocketCallback :
                                MicroWebSocket( socket         = self._socket,
                                                httpClient     = self,
                                                httpResponse   = response,
                                                maxRecvLen     = self._microWebSrv.MaxWebSocketRecvLen,
                                                threaded       = self._microWebSrv.WebSocketThreaded,
                                                acceptCallback = self._microWebSrv.AcceptWebSocketCallback )
                                return
                        else :
                            response.WriteResponseNotImplemented()
                    else :
                        response.WriteResponseBadRequest()
            except :
                response.WriteResponseInternalServerError()
            try :
                if self._socketfile is not self._socket:
                    self._socketfile.close()
                self._socket.close()
            except :
                pass

        # ------------------------------------------------------------------------

        def _parseFirstLine(self, response):
            """
            The simple helper method parses the first line received from the client e.g. "Get /mypath/myfolder/file?parm=2 HTTP/1.1"
            It then extracts the HTTP method (GET,PUT,POST,DELETE) the path requested /mypath/myfolder/file and querry
            parameters parm =2.
            Values are stored in object variables:
                _method
                _path
                _httpVer
                _queryParams

             Returns 'True' if successful.

            :param response:
            :return: Boolean
            """
            try :
                elements = self._socketfile.readline().decode().strip().split()     # Parsing HTTP line e.g. ['GET', '/', 'HTTP/1.1']
                if len(elements) == 3 :
                    self._method  = elements[0].upper()
                    self._path    = elements[1]
                    self._httpVer = elements[2].upper()
                    elements      = self._path.split('?', 1)                        # Split querry parms e.g. /mypath/path/end?for=2
                    log.info("Processing request HTTP Method: %s Path: %s Version: %s", self._method, self._path, self._httpVer)
                    if len(elements) > 0 :
                        self._resPath = MicroWebSrv._unquote_plus(elements[0])
                        if len(elements) > 1 :
                            self._queryString = elements[1]
                            elements = self._queryString.split('&')
                            for s in elements :
                                param = s.split('=', 1)
                                if len(param) > 0 :
                                    value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
                                    self._queryParams[MicroWebSrv._unquote(param[0])] = value
                    return True
            except :
                pass
            return False
    
        # ------------------------------------------------------------------------

        def _parseHeader(self, response):
            """
            Takes a HTTP header and populates the dictionary item self._headers from the incoming request. It does this by
            doing a socket.readline(). The HTTP header is put in the dictionary e.g.

            {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Mobile Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'upgrade-insecure-requests': '1',
            'cookie': 'cookielaw_accepted=1',
            'cache-control': 'no-cache',
            'connection': 'keep-alive',
            'pragma': 'no-cache',
            'accept-encoding': 'gzip, deflate, br',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-fetch-user': '?1',
            'host': 'localhost:8001'}

            :param response:
            :return: Boolean

            """
            while True :
                elements = self._socketfile.readline().decode().strip().split(':', 1)
                if len(elements) == 2 :
                    self._headers[elements[0].strip().lower()] = elements[1].strip()
                elif len(elements) == 1 and len(elements[0]) == 0 :
                    if self._method == 'POST' or self._method == 'PUT' :
                        self._contentType   = self._headers.get("content-type", None)
                        self._contentLength = int(self._headers.get("content-length", 0))
                    return True
                else :
                    return False

        # ------------------------------------------------------------------------

        def _getConnUpgrade(self):
            if 'upgrade' in self._headers.get('connection', '').lower() :
                return self._headers.get('upgrade', '').lower()
            return None

        # ------------------------------------------------------------------------

        def GetServer(self):
            return self._microWebSrv

        # ------------------------------------------------------------------------

        def GetAddr(self):
            return self._addr

        # ------------------------------------------------------------------------

        def GetIPAddr(self):
            return self._addr[0]

        # ------------------------------------------------------------------------

        def GetPort(self):
            return self._addr[1]

        # ------------------------------------------------------------------------

        def GetRequestMethod(self):
            return self._method

        # ------------------------------------------------------------------------

        def GetRequestTotalPath(self):
            return self._path

        # ------------------------------------------------------------------------

        def GetRequestPath(self):
            return self._resPath

        # ------------------------------------------------------------------------

        def GetRequestQueryString(self):
            return self._queryString

        # ------------------------------------------------------------------------

        def GetRequestQueryParams(self):
            return self._queryParams

        # ------------------------------------------------------------------------

        def GetRequestHeaders(self):
            return self._headers

        # ------------------------------------------------------------------------

        def GetRequestContentType(self):
            return self._contentType

        # ------------------------------------------------------------------------

        def GetRequestContentLength(self):
            return self._contentLength

        # ------------------------------------------------------------------------

        def ReadRequestContent(self, size=None):
            self._socket.setblocking(False)
            b = None
            try :
                if not size :
                    b = self._socketfile.read(self._contentLength)
                elif size > 0 :
                    b = self._socketfile.read(size)
            except :
                pass
            self._socket.setblocking(True)
            return b if b else b''

        # ------------------------------------------------------------------------

        def ReadRequestPostedFormData(self):
            res  = { }
            data = self.ReadRequestContent()
            if len(data) > 0 :
                elements = data.decode().split('&')
                for s in elements :
                    param = s.split('=', 1)
                    if len(param) > 0 :
                        value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
                        res[MicroWebSrv._unquote(param[0])] = value
            return res

        # ------------------------------------------------------------------------

        def ReadRequestContentAsJSON(self):
            try :
                return loads(self.ReadRequestContent())
            except :
                return None
        
    # ============================================================================
    # ===( Class Response  )======================================================
    # ============================================================================

    class _response:

        # ------------------------------------------------------------------------

        def __init__(self, client) :
            self._client = client

        # ------------------------------------------------------------------------

        def _write(self, data):
            if data :
                if type(data) == str :
                    data = data.encode()
                return self._client._socketfile.write(data)
            return 0

        # ------------------------------------------------------------------------

        def _writeFirstLine(self, code):
            reason = self._responseCodes.get(code, ('Unknown reason', ))[0]
            self._write("HTTP/1.1 %s %s\r\n" % (code, reason))

        # ------------------------------------------------------------------------

        def _writeHeader(self, name, value):
            self._write("%s: %s\r\n" % (name, value))

        # ------------------------------------------------------------------------

        def _writeContentTypeHeader(self, contentType, charset=None):
            if contentType :
                ct = contentType \
                   + (("; charset=%s" % charset) if charset else "")
            else :
                ct = "application/octet-stream"
            self._writeHeader("Content-Type", ct)

        # ------------------------------------------------------------------------

        def _writeServerHeader(self):
            self._writeHeader("Server", "MicroWebSrv by JC`zic")

        # ------------------------------------------------------------------------

        def _writeEndHeader(self):
            self._write("\r\n")

        # ------------------------------------------------------------------------

        def _writeBeforeContent(self, code, headers, contentType, contentCharset, contentLength):
            self._writeFirstLine(code)
            if isinstance(headers, dict) :
                for header in headers :
                    self._writeHeader(header, headers[header])
            if contentLength > 0 :
                self._writeContentTypeHeader(contentType, contentCharset)
                self._writeHeader("Content-Length", contentLength)
            self._writeServerHeader()
            self._writeHeader("Connection", "close")
            self._writeEndHeader()

        # ------------------------------------------------------------------------

        def WriteSwitchProto(self, upgrade, headers=None):
            self._writeFirstLine(101)
            self._writeHeader("Connection", "Upgrade")
            self._writeHeader("Upgrade",    upgrade)
            if isinstance(headers, dict) :
                for header in headers :
                    self._writeHeader(header, headers[header])
            self._writeServerHeader()
            self._writeEndHeader()
            if self._client._socketfile is not self._client._socket :
                self._client._socketfile.flush()   # CPython needs flush to continue protocol

        # ------------------------------------------------------------------------

        def WriteResponse(self, code, headers, contentType, contentCharset, content):
            """
            The main method to create a HTTP response object. It takes parameters:
             - HTTP code (e.g. 200, 404, etc...);
             - headers;
             - content type (e.g. text/html);
             - character set (e.g. UTF-9); and
             content and constructs a HTTP response object. It first sends a header over a socket interface responsible for sending reason code,
             http version, method response and size of the content.
             It then sends the content over a socket interface.

            :param HTTP code (e.g. 200, 404, etc...);
            :param headers:
            :param contentType: (e.g. text/html)
            :param contentCharset:  (e.g. UTF-9)
            :param content:
            :return: Boolean
            """
            try :
                if content :
                    if type(content) == str :
                        content = content.encode()
                    contentLength = len(content)
                else :
                    contentLength = 0
                log.debug("Server writing response via route handler. Response code: %d Content Length: %d", code, contentLength)
                self._writeBeforeContent(code, headers, contentType, contentCharset, contentLength)
                if content :
                    self._write(content)
                return True
            except Exception as e:
                log.exc(e, "Problem sending response via route handler. Response code (%d) Content Length: (%d)", code, contentLength)
                return False

        # ------------------------------------------------------------------------

        def WriteResponsePyHTMLFile(self, filepath, headers=None, vars=None):
            if 'MicroWebTemplate' in globals() :
                with open(filepath, 'r') as file :
                    code = file.read()
                mWebTmpl = MicroWebTemplate(code, escapeStrFunc=MicroWebSrv.HTMLEscape, filepath=filepath)
                try :
                    tmplResult = mWebTmpl.Execute(None, vars)
                    return self.WriteResponse(200, headers, "text/html", "UTF-8", tmplResult)
                except Exception as ex :
                    return self.WriteResponse( 500,
    	                                       None,
    	                                       "text/html",
    	                                       "UTF-8",
    	                                       self._execErrCtnTmpl % {
    	                                            'module'  : 'PyHTML',
    	                                            'message' : str(ex)
    	                                       } )
            return self.WriteResponseNotImplemented()

        # ------------------------------------------------------------------------

        def WriteResponseFile(self, filepath, contentType=None, headers=None):
            """
            A method to write a file to the client. It takes the path of the file, calculates it's size and copies the file in chunk
            sizes of 1024 octets via the low level socket interface. The method first builds the first line of the HTTP request and
            provides headers, content type, reason code and size of the file. It then does the sending of the file in 1024 octet chunks
            to the client.
            If there is a failure in reading the file a WriteREsponseNotFound is sent.
            If there is a faulure in sending the file to the client a WriteResponseInternalServerError is sent.

            :param filepath:    (e.g. www/style.css)
            :param contentType: (e.g. text/html)
            :param headers:     (e.g. {'Cache-Control': 'max-age=315360000', 'Last-Modified': 'Fri, 1 Jan 2018 23:42:00 GMT'})
            :return: Boolean
            """
            try :
                size = stat(filepath)[6]
                log.debug("Server writing file: %s of size: %s of type: %s to host: %s", filepath, size, contentType, self._client._addr)
                if size > 0 :
                    with open(filepath, 'rb') as file :                                 # Open file for reading in binary mode
                        self._writeBeforeContent(200, headers, contentType, None, size) # Write our HTTP header
                        try :
                            buf = bytearray(1024)
                            while size > 0 :
                                x = file.readinto(buf)
                                if x < len(buf) :
                                    buf = memoryview(buf)[:x]
                                    log.debug("Last: %d octets being sent", x)
                                self._write(buf)                                        # call up low level socket write function
                                size -= x
                            return True
                        except Exception as e:
                            log.exc(e, "Problem sending file: (%s) of size: (%d)", filepath, size)
                            self.WriteResponseInternalServerError()
                            return False
            except :
                pass
            self.WriteResponseNotFound()
            return False

        # ------------------------------------------------------------------------

        def WriteResponseFileAttachment(self, filepath, attachmentName, headers=None):
            if not isinstance(headers, dict) :
                headers = { }
            headers["Content-Disposition"] = "attachment; filename=\"%s\"" % attachmentName
            return self.WriteResponseFile(filepath, None, headers)

        # ------------------------------------------------------------------------

        def WriteResponseOk(self, headers=None, contentType=None, contentCharset=None, content=None):
            return self.WriteResponse(200, headers, contentType, contentCharset, content)

        # ------------------------------------------------------------------------

        def WriteResponseJSONOk(self, obj=None, headers=None):
            return self.WriteResponse(200, headers, "application/json", "UTF-8", dumps(obj))

        # ------------------------------------------------------------------------

        def WriteResponseRedirect(self, location):
            headers = { "Location" : location }
            return self.WriteResponse(302, headers, None, None, None)

        # ------------------------------------------------------------------------

        def WriteResponseError(self, code):
            responseCode = self._responseCodes.get(code, ('Unknown reason', ''))
            return self.WriteResponse( code,
                                       None,
                                       "text/html",
                                       "UTF-8",
                                       self._errCtnTmpl % {
                                            'code'    : code,
                                            'reason'  : responseCode[0],
                                            'message' : responseCode[1]
                                       } )

        # ------------------------------------------------------------------------

        def WriteResponseJSONError(self, code, obj=None):
            return self.WriteResponse( code,
                                       None,
                                       "application/json",
                                       "UTF-8",
                                       dumps(obj if obj else { }) )

        # ------------------------------------------------------------------------

        def WriteResponseNotModified(self):
            return self.WriteResponseError(304)

        # ------------------------------------------------------------------------

        def WriteResponseBadRequest(self):
            return self.WriteResponseError(400)

        # ------------------------------------------------------------------------

        def WriteResponseForbidden(self):
            return self.WriteResponseError(403)

        # ------------------------------------------------------------------------

        def WriteResponseNotFound(self):
            log.warning("A resource was requested but not found. Server responded with a HTTP 404")
            if self._client._microWebSrv._notFoundUrl :
                self.WriteResponseRedirect(self._client._microWebSrv._notFoundUrl)
            else :
                return self.WriteResponseError(404)

        # ------------------------------------------------------------------------

        def WriteResponseMethodNotAllowed(self):
            return self.WriteResponseError(405)

        # ------------------------------------------------------------------------

        def WriteResponseInternalServerError(self):
            log.error("An internal server error happened. Server responded with a HTTP 500")
            return self.WriteResponseError(500)

        # ------------------------------------------------------------------------

        def WriteResponseNotImplemented(self):
            return self.WriteResponseError(501)

        # ------------------------------------------------------------------------

        def FlashMessage(self, messageText, messageStyle=''):
            if 'MicroWebTemplate' in globals() :
                MicroWebTemplate.MESSAGE_TEXT = messageText
                MicroWebTemplate.MESSAGE_STYLE = messageStyle

        # ------------------------------------------------------------------------

        _errCtnTmpl = """\
        <html>
            <head>
                <title>Error</title>
            </head>
            <body>
                <h1>%(code)d %(reason)s</h1>
                %(message)s
            </body>
        </html>
        """

        # ------------------------------------------------------------------------

        _execErrCtnTmpl = """\
        <html>
            <head>
                <title>Page execution error</title>
            </head>
            <body>
                <h1>%(module)s page execution error</h1>
                %(message)s
            </body>
        </html>
        """

        # ------------------------------------------------------------------------

        _responseCodes = {
            100: ('Continue', 'Request received, please continue'),
            101: ('Switching Protocols',
                  'Switching to new protocol; obey Upgrade header'),

            200: ('OK', 'Request fulfilled, document follows'),
            201: ('Created', 'Document created, URL follows'),
            202: ('Accepted',
                  'Request accepted, processing continues off-line'),
            203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
            204: ('No Content', 'Request fulfilled, nothing follows'),
            205: ('Reset Content', 'Clear input form for further input.'),
            206: ('Partial Content', 'Partial content follows.'),

            300: ('Multiple Choices',
                  'Object has several resources -- see URI list'),
            301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
            302: ('Found', 'Object moved temporarily -- see URI list'),
            303: ('See Other', 'Object moved -- see Method and URL list'),
            304: ('Not Modified',
                  'Document has not changed since given time'),
            305: ('Use Proxy',
                  'You must use proxy specified in Location to access this '
                  'resource.'),
            307: ('Temporary Redirect',
                  'Object moved temporarily -- see URI list'),

            400: ('Bad Request',
                  'Bad request syntax or unsupported method'),
            401: ('Unauthorized',
                  'No permission -- see authorization schemes'),
            402: ('Payment Required',
                  'No payment -- see charging schemes'),
            403: ('Forbidden',
                  'Request forbidden -- authorization will not help'),
            404: ('Not Found', 'Nothing matches the given URI'),
            405: ('Method Not Allowed',
                  'Specified method is invalid for this resource.'),
            406: ('Not Acceptable', 'URI not available in preferred format.'),
            407: ('Proxy Authentication Required', 'You must authenticate with '
                  'this proxy before proceeding.'),
            408: ('Request Timeout', 'Request timed out; try again later.'),
            409: ('Conflict', 'Request conflict.'),
            410: ('Gone',
                  'URI no longer exists and has been permanently removed.'),
            411: ('Length Required', 'Client must specify Content-Length.'),
            412: ('Precondition Failed', 'Precondition in headers is false.'),
            413: ('Request Entity Too Large', 'Entity is too large.'),
            414: ('Request-URI Too Long', 'URI is too long.'),
            415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
            416: ('Requested Range Not Satisfiable',
                  'Cannot satisfy request range.'),
            417: ('Expectation Failed',
                  'Expect condition could not be satisfied.'),

            500: ('Internal Server Error', 'Server got itself in trouble'),
            501: ('Not Implemented',
                  'Server does not support this operation'),
            502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
            503: ('Service Unavailable',
                  'The server cannot process the request due to a high load'),
            504: ('Gateway Timeout',
                  'The gateway server did not receive a timely response'),
            505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        }

    # ============================================================================
    # ============================================================================
    # ============================================================================

