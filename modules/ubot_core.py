###########
## IMPORTS

import esp, gc, network, ujson, uos, usocket, sys, webrepl

from machine     import Pin, PWM, RTC, Timer, UART, WDT
from ubinascii   import hexlify
from utime       import sleep, sleep_ms

import ubot_feedback  as feedback
import ubot_turtlehat as turtlehat
import ubot_webserver as webserver

from ubot_buzzer     import Buzzer
from ubot_motor      import Motor


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

PRESSED_BUTTONS = []

LSM303_LOG = ""

################################
## METHODS

def executeJson(json):
    global MOT
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
                results.append("'{}' executed successfully, the result is: '{}'".format(command, eval(command[5:])))

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

    return results


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


def saveToFile(fileName, mode, content):
    global DT
    global EXCEPTIONS
    try:
        with open(fileName, mode) as file:
            file.write(content)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))

def saveDateTime():
    global DT
    saveToFile("etc/datetime.py", "w", "DT = {}".format(DT.datetime()))


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


def startLsmTest():
    global TEST_LSM
    LSM303_LOG = "etc/LSM303__" + str(DT.datetime()).replace(", ", "_")

    while LSM303_LOG != "":
        result = feedback._test()
        saveToFile(LSM303_LOG, "a+", str(result)+"\n")
        print(result)
        sleep_ms(100)

def stopLsmTest():
    LSM303_LOG = ""


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
        feedback.config(CONFIG.get("i2cFreq"), Pin(CONFIG.get("i2cSda")), Pin(CONFIG.get("i2cScl")))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))



###########
## GPIO

BUZZ = Buzzer(Pin(15), 262, 0, CONFIG.get("buzzerActive"))


if CONFIG.get("turtleHatActive"):
    turtlehat.config(CONFIG, PRESSED_BUTTONS, BUZZ)
else:
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On turtle HAT it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


if not CONFIG.get("i2cActive"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


motorConfig = (
    (CONFIG.get("motorT0Period"),     CONFIG.get("motorT0Sleep")),
    (CONFIG.get("motorT1Frequency"),  CONFIG.get("motorT1Duty")),
    (CONFIG.get("motorT1DutyFactor"), CONFIG.get("motorT1MinDuty"), CONFIG.get("motorT1MaxDuty"))
)

motorPins  = (
    (0, 0) if CONFIG.get("uartActive") else (1, 3),
    (4, 5)
)

MOT = Motor(motorConfig, motorPins)



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

socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
socket.bind(("", 80))
socket.listen(5)

webserver.config(socket, DT, CONFIG, EXCEPTIONS, executeJson)


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
    #TIMER_SERVER.init(period = 1000, mode = Timer.PERIODIC, callback = lambda t:tryCheckWebserver())
    webserver.start()
