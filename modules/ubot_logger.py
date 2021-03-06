"""
    uBot_firmware   // The firmware of the μBot, the educational floor robot. (A MicroPython port to ESP8266 with additional modules.)

    This file is part of uBot_firmware.
    [https://zza.hu/uBot_firmware]
    [https://git.zza.hu/uBot_firmware]


    MIT License

    Copyright (c) 2020-2021 Szabó László András <hu@zza.hu>

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

import uos, usys

from machine import RTC

import ubot_config as config


_fileName = 0
                #    Name   | List |   Directory
_logFiles = (
                ["Exception", [], "log/exception/"],
                ["Event",     [], "log/event/"],
                ["Object",    [], "log/object/"]
            )



################################
## PUBLIC METHODS

def append(item):
    if _fileName != 0:
        try:
            with open(_logFiles[_defineIndex(item)][2] + _fileName, "a") as file:
                _writeOutItem(config.datetime(), file, item)
        except Exception as e:
            _appendToList(e)
            _appendToList(item)
    else:
        _appendToList(item)



################################
## PRIVATE, HELPER METHODS

def _appendToList(item):
    global _logFiles

    index = _defineIndex(item)

    try:
        _logFiles[index][1].append((config.datetime(), item))

        if 30 < len(_logFiles[index][1]):
            try:
                _saveFromList(_logFiles[index])
            except Exception as e:
                _logFiles[index][1] = _logFiles[index][1][10:]              # Reassign list (Delete the oldest 10 items.)

    except Exception as e:
        usys.print_exception(e)
        if index == 0:
            usys.print_exception(item)


def _saveFromList(logFile, fallback = False):
    if logFile[1] != []:                                            # If this list contains item(s).

        if _fileName == 0:                                          # If filename is undefined.
            fallback = True

        fileName = "0000000000.txt" if fallback else _fileName
        try:
            with open(logFile[2] + fileName, "a") as file:
                for item in logFile[1]:
                    _writeOutItem(item[0], file, item[1])
            logFile[1] = []
        except Exception as e:
            usys.print_exception(e)

            if not fallback:
                _saveFromList(logFile, True)


def _writeOutItem(dateTime, file, item):
    file.write("{}\n".format(dateTime))

    if _defineIndex(item) == 0:
        usys.print_exception(item, file)
    else:
        if isinstance(item, list):
            for i in item:
                file.write("{}\n".format(i))
        else:
            file.write("{}\n".format(item))

    file.write("\n")


def _defineIndex(item):
    if isinstance(item, Exception):
        return 0
    elif isinstance(item, dict):
        return 2
    else:
        return 1



################################
## INITIALISATION

_fileName = "{:010d}.txt".format(int(config.get("system", "powerOnCount")))

try:
    with open("log/datetime.txt", "a") as file:
        file.write("{}\n{}\n\n".format(config.datetime(), _fileName))
except Exception as e:
    _appendToList(e)

for logFile in _logFiles:
    try:
        with open(logFile[2] + _fileName, "w") as file:
            file.write("{}\n{} log initialised successfully.\n\n".format(config.datetime(), logFile[0]))
            _saveFromList(logFile)
    except Exception as e:
        _appendToList(e)
