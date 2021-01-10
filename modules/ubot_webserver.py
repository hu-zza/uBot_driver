import gc, ujson

from machine import RTC

import ubot_webpage_template


_socket       = 0
_dateTime     = 0
_config       = 0
_exceptions   = 0
_jsonFunction = 0
_connection   = 0
_address      = 0

def config(socket, dateTime, config, exceptionList, jsonFunction):
    global _socket
    global _dateTime
    global _config
    global _exceptions
    global _jsonFunction

    _socket       = socket
    _dateTime     = dateTime
    _config       = config
    _exceptions   = exceptionList
    _jsonFunction = jsonFunction


def _getDebugTable(method, path, length = 0, type = "-", body = "-"):
    length = str(length)

    result = ubot_webpage_template.getStats()

    allMem = gc.mem_free() + gc.mem_alloc()
    freePercent = gc.mem_free() * 100 // allMem

    exceptionList = "<table class=\"exceptions\"><colgroup><col><col><col></colgroup><tbody>"
    index = 0

    for (dt, exception) in _exceptions:
        exceptionList += "<tr><td> {} </td><td> {}. {}. {}. {}:{}:{}.{} </td><td> {} </td></tr>".format(
            index, dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[7], exception
        )
        index += 1

    exceptionList += "</tbody></table>"

    return result.format(
        method = method, path = path, length = length, type = type, body = body,
        freePercent = freePercent, freeMem = gc.mem_free(), allMem = allMem, exceptions = exceptionList
    )


def _reply(returnFormat, httpCode, message, title = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    try:
        _connection.send("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        _connection.send("Content-Type: " + str + "\r\n")
        _connection.send("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            if title == None:
                title = httpCode
            str  = "<html><head><title>" + title + "</title><style>"
            str += ubot_webpage_template.getStyle()
            str += "</style></head>"
            str += "<body><h1>" + httpCode + "</h1><p>" + message + "</p></body></html>\r\n\r\n"
        elif returnFormat == "JSON":
            str = ujson.dumps({"code" : httpCode, "message" : message})

        _connection.sendall(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        _connection.close()


def _processGetQuery(path):
    _reply("HTML", "200 OK", _getDebugTable("GET", path), "&microBot Debug Page")


def _processPostQuery(body):
    try:
        json = ujson.loads(body)

        if json.get("estimatedExecutionTime") != None:
            if 10 < json.get("estimatedExecutionTime"):
                _reply("JSON", "200 OK", "JSON parsed, execution in progress.")

        _reply("JSON", "200 OK", _jsonFunction(json))
    except Exception as e:
        _exceptions.append((_dateTime.datetime(), e))
        _reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.")


def _processSockets():
    global _connection
    global _address

    method        = ""
    path          = ""
    contentLength = 0
    contentType   = ""
    body          = ""

    _connection, _address  = _socket.accept()
    requestFile = _connection.makefile("rwb", 0)

    try:
        while True:
            line = requestFile.readline()

            if not line:
                break
            elif line == b"\r\n":
                if 0 < contentLength:
                    body = str(requestFile.read(contentLength), "utf-8")
                break

            line = str(line, "utf-8")

            if method == "":
                firstSpace = line.find(" ")
                pathEnd    = line.find(" HTTP")

                method = line[0:firstSpace]
                path   = line[firstSpace+1:pathEnd]

            if 0 <= line.lower().find("content-length:"):
                contentLength = int(line[15:].strip())

            if 0 <= line.lower().find("content-type:"):
                contentType = line[13:].strip()

        if method == "GET":
            _processGetQuery(path)
        elif method == "POST":
            if contentType == "application/json":
                _processPostQuery(body)
            else:
                _reply("HTML", "400 Bad Request", "'Content-Type' should be 'application/json'.")
        else:
            _reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and PUT) are allowed.")
    finally:
        _connection.close()


def start():
    global _config

    _config['webServerActive'] = True

    if _config.get("apActive"):
        while _config.get("webServerActive"):
            try:
                _processSockets()
            except Exception as e:
                _exceptions.append((_dateTime.datetime(), e))


def stop(message):
    global _config

    if _config.get("webServerActive"):
        try:
            _reply("JSON", "200 OK", [message])
            _config['webServerActive'] = False
        except Exception as e:
            _exceptions.append((_dateTime.datetime(), e))
