###########
## IMPORTS

import esp, gc, network, ujson, uos, usocket, sys, webrepl

from machine     import Pin, PWM, RTC, Timer, UART, WDT
from ubinascii   import hexlify
from utime       import sleep, sleep_ms


import ubot_webpage_template

from ubot_buzzer     import Buzzer
from ubot_motor      import Motor
from ubot_feedback   import Feedback
from ubot_turtlehat  import TurtleHAT

# Import configuration files
EXCEPTIONS     = []
datetimeLoaded = True
configLoaded   = True
defaultsLoaded = True

try:
    import etc.datetime as datetime
except Exception as e:
    datetimeLoaded = False
    EXCEPTIONS.append(([], e))

try:
    import etc.config as config
except Exception as e:
    configLoaded = False
    EXCEPTIONS.append(([], e))

try:
    import etc.defaults as defaults
except Exception as e:
    defaultsLoaded = False
    EXCEPTIONS.append(([], e))



###########
## GLOBALS

DT = IDT = RTC()

TIMER_SERVER = Timer(-1)

CONFIG = {}

CONN  = ""
ADDR  = ""

COUNTER_POS  = 0
COMMAND_LIST = []
EVALS        = []



################################
## METHODS

# Adding datetime afterwards to exceptions
def replaceNullDT():
    global DT
    global EXCEPTIONS
    for i in range(len(EXCEPTIONS)):
        if len(EXCEPTIONS[i][0]) == 0:                                 # If datetime is an empty collection
            EXCEPTIONS[i] = (DT.datetime(), EXCEPTIONS[i][1])          # Reassign exception with datetime

def listExceptions():
    for i in range(len(EXCEPTIONS)):
        print("{}\t{}\t{}".format(i, EXCEPTIONS[i][0], EXCEPTIONS[i][1]))


def printException(nr):
    if 0 <= nr and nr < len(EXCEPTIONS):
        print(EXCEPTIONS[nr][0])
        sys.print_exception(EXCEPTIONS[nr][1])
    else:
        print("List index ({}) is out of range ({}).".format(nr, len(EXCEPTIONS)))


def saveToFile(fileName, content):
    global DT
    global EXCEPTIONS
    try:
        with open(fileName, "w") as file:
            file.write(content)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))

def saveDateTime():
    global DT
    saveToFile("etc/datetime.py", "DT = {}".format(DT.datetime()))


def saveConfig():
    global CONFIG
    global DT
    global EXCEPTIONS
    try:
        with open("etc/config.py", "w") as file:

            for key in sorted([k for k in CONFIG.keys()]):
                value = CONFIG.get(key)
                if isinstance(value, str):
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))
    except Exception as e:
        EXCEPTIONS.append(e)




def tryCheckButtons():
    global DT
    global EXCEPTIONS
    try:
        checkButtons()
    except Exception as e:
        if len(EXCEPTIONS) < 20:
            EXCEPTIONS.append((DT.datetime(), e))


def tryCheckWebserver():
    global CONFIG
    global DT
    global EXCEPTIONS
    try:
        if CONFIG.get("watchdogActive") and AP.active():             # TODO: Some more sophisticated checks needed.
            global WD
            WD.feed()
    except Exception as e:
        if len(EXCEPTIONS) < 20:
            EXCEPTIONS.append((DT.datetime(), e))



def getDebugTable(method, path, length = 0, type = "-", body = "-"):
    global DT
    global EXCEPTIONS

    length = str(length)

    result = ubot_webpage_template.getStats()

    allMem = gc.mem_free() + gc.mem_alloc()
    freePercent = gc.mem_free() * 100 // allMem


    exceptionList = "<table class=\"exceptions\"><colgroup><col><col><col></colgroup><tbody>"
    index = 0

    for (dt, exception) in EXCEPTIONS:
        exceptionList += "<tr><td> {} </td><td> {}. {}. {}. {}:{}:{}.{} </td><td> {} </td></tr>".format(
            index, dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[7], exception
        )
        index += 1

    exceptionList += "</tbody></table>"

    return result.format(
        method = method, path = path, length = length, type = type, body = body,
        freePercent = freePercent, freeMem = gc.mem_free(), allMem = allMem,
        commands = COMMAND_LIST, evals = EVALS, exceptions = exceptionList
    )


def reply(returnFormat, httpCode, message, title = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    global CONN

    try:
        CONN.send("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        CONN.send("Content-Type: " + str + "\r\n")
        CONN.send("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            if title == None:
                title = httpCode
            str  = "<html><head><title>" + title + "</title><style>"
            str += ubot_webpage_template.getStyle()
            str += "</style></head>"
            str += "<body><h1>" + httpCode + "</h1><p>" + message + "</p></body></html>\r\n\r\n"
        elif returnFormat == "JSON":
            str = ujson.dumps({"code" : httpCode, "message" : message})

        CONN.sendall(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        CONN.close()


def togglePin(pin):
    pin.value(1 - pin.value())


def processJson(json):
    global CONFIG
    global DT
    global BUZZ
    global MOT
    global EVALS
    results = []

    if json.get("dateTime") != None:
        DT.datetime(eval(json.get("dateTime")))
        saveDateTime()
        results.append("New dateTime has been set.")

    if json.get("commandList") != None:
        for command in json.get("commandList"):
            if command[0:5] == "SLEEP":
                sleep_ms(int(command[5:].strip()))
                results.append("'{}' executed successfully.".format(command))
            elif command[0:5] == "BEEP_":
                BUZZ.beep(int(command[5:].strip()), 2, 4)
                results.append("'{}' executed successfully.".format(command))
            elif command[0:5] == "MIDI_":
                BUZZ.midiBeep(int(command[5:].strip()), 2, 4)
                results.append("'{}' executed successfully.".format(command))
            elif command[0:5] == "EXEC_": ##############################################################################
                exec(command[5:])
                results.append("'{}' executed successfully.".format(command))
            elif command[0:5] == "EVAL_": ##############################################################################
                r = eval(command[5:])
                EVALS.append(r)
                results.append("'{}' executed successfully, the result is: '{}'".format(command, r))

    if json.get("service") != None:
            for command in json.get("service"):
                if command == "START UART":
                    uart = UART(0, 115200)
                    uos.dupterm(uart, 1)
                    CONFIG['uartActive'] = True
                    results.append("UART has started.")
                elif command == "STOP UART":
                    uos.dupterm(None, 1)
                    CONFIG['uartActive'] = False
                    results.append("UART has stopped.")
                elif command == "START WEBREPL":
                    webrepl.start()
                    CONFIG['webReplActive'] = True
                    results.append("WebREPL has started.")
                elif command == "STOP WEBREPL":
                    webrepl.stop()
                    CONFIG['webReplActive'] = False
                    results.append("WebREPL has stopped.")
                elif command == "STOP WEBSERVER":
                    stopWebServer("WebServer has stopped.")
                elif command == "CHECK DATETIME":
                    results.append(str(DT.datetime()))
                elif command == "SAVE CONFIG":
                    saveConfig()
                    results.append("Configuration has saved.")

    if len(results) == 0:
        results = ["Processing has completed without any result."]

    reply("JSON", "200 OK", results)


def processGetQuery(path):
    reply("HTML", "200 OK", getDebugTable("GET", path), "uBot Debug Page")


def processPostQuery(body):
    global DT
    global EXCEPTIONS
    try:
        json = ujson.loads(body)

        if json.get("execute") == True:
            reply("JSON", "200 OK", "JSON parsed, execution in progress.")

        processJson(json)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
        reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.")


def processSockets():
    global CONN
    global ADDR

    method = ""
    path = ""
    contentLength = 0
    contentType = ""
    body = ""

    CONN, ADDR  = S.accept()
    requestFile = CONN.makefile("rwb", 0)

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
            processGetQuery(path)
        elif method == "POST":
            if contentType == "application/json":
                processPostQuery(body)
            else:
                reply("HTML", "400 Bad Request", "'Content-Type' should be 'application/json'.")
        else:
            reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and PUT) are allowed.")
    finally:
        CONN.close()


def startWebServer():
    global CONFIG
    global DT
    global EXCEPTIONS

    CONFIG['webServerActive'] = True

    if CONFIG.get("apActive"):
        while CONFIG.get("webServerActive"):
            try:
                processSockets()                        #TODO: uselect, poll, etc
            except Exception as e:
                EXCEPTIONS.append((DT.datetime(), e))


def stopWebServer(message):
    global CONFIG
    global DT
    global EXCEPTIONS

    if CONFIG.get("webServerActive"):
        try:
            reply("JSON", "200 OK", [message])
            CONFIG['webServerActive'] = False
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))



################################
## INITIALISATION

gc.enable()
esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)

if datetimeLoaded:
    try:
        DT.datetime(datetime.DT)
    except Exception as e:
        EXCEPTIONS.append(([], e))


if configLoaded or defaultsLoaded:
    if configLoaded:
        conf = "config"
    else:
        conf = "defaults"
        EXCEPTIONS.append(([], "Can not import configuration file, default values have been loaded."))

    # Fetch every variable from config.py / defaults.py
    for v in dir(eval(conf)):
        if v[0] != "_":
            CONFIG[v] = eval("{}.{}".format(conf, v))

    # If etc/datetime.py is not accessible, set the DT to 'initialDateTime'.
    if not datetimeLoaded:
        DT.datetime(CONFIG["initialDateTime"])

    IDT = DT.datetime()

    replaceNullDT()
else:
    replaceNullDT()
    EXCEPTIONS.append((DT.datetime(), "Neither the configuration file, nor the default values can be loaded."))

if CONFIG.get("i2cActive"):
    try:
        F = Feedback(CONFIG.get("i2cFreq"), Pin(CONFIG.get("i2cSda")), Pin(CONFIG.get("i2cScl")))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))



###########
## GPIO

BUZZ = Buzzer(Pin(15), 262, 0, CONFIG.get("buzzerActive"))


if CONFIG.get("turtleHatActive"):
    TURTLE_HAT = TurtleHAT(CONFIG, COMMAND_LIST, BUZZ)
else:
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On turtle HAT it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


P4 = Pin(4, Pin.OUT)        # Connected to the 10th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P5 = Pin(5, Pin.OUT)        # Connected to the 15th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P4.off()
P5.off()

motorPins = [[P4, P5], [P4, P5]]

if not CONFIG.get("uartActive"):
    motorPins[0][0] = P1 = Pin(1, Pin.OUT) # Connected to the  2nd pin of the motor driver (SN754410). T0 terminal (M3, M6)
    motorPins[0][1] = P3 = Pin(3, Pin.OUT) # Connected to the  7th pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P1.off()
    P3.off()

MOT = Motor(motorPins[0][0], motorPins[0][1], motorPins[1][0], motorPins[1][1])

if not CONFIG.get("i2cActive"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)



###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(CONFIG.get("apActive"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

try:
    AP.config(essid = CONFIG.get("apEssid"))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))

try:
    AP.config(password = CONFIG.get("apPassword"))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))



###########
## SOCKET

S = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
S.bind(("", 80))
S.listen(5)



###########
## GENERAL

if CONFIG.get("watchdogActive"):
    WD = WDT()

# The REPL is attached by default to UART0, detach if not needed.
if not CONFIG.get("uartActive"):
    uos.dupterm(None, 1)

if CONFIG.get("webReplActive"):
    try:
        webrepl.start()
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


if CONFIG.get("webServerActive"):
    TIMER_SERVER.init(period = 1000, mode = Timer.PERIODIC, callback = lambda t:tryCheckWebserver())
    startWebServer()
