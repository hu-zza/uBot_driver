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

import gc, uos

import ubot_config as config
import ubot_turtle as turtle



###########
## GENERAL

def getSimplePage():
    return ("<!DOCTYPE html>\n"
            "<html>\n"
            "    <head>\n"
            "        <meta name='viewport' content='width=450'>\n"
            "        <meta charset='utf-8'>\n"
            "        <title>{title}</title>\n"
            "        <style>\n"
            "{style}"
            "        </style>\n"
            "    </head>\n"
            "    <body>\n"
            "        <h1>{title}</h1>\n"
            "        {body}\n"
            "    </body>\n"
            "</html>\r\n\r\n"
           )


def getPageHeadStart():
    return ("<!DOCTYPE html>\n"
            "<html>\n"
            "    <head>\n"
            "        <meta name='viewport' content='width=610'>\n"
            "        <meta charset='utf-8'>\n"
            "        <title>{}</title>\n"
            "        <style>\n"
           )


def getPageHeadEnd():
    return ("        </style>\n"
            "    </head>\n"
            "    <body>\n"
           )


def getPageFooter():
    return ("    </body>\n"
            "</html>\r\n\r\n"
           )


def getGeneralStyle():
    return ("            body     { font-family: Garamond, Baskerville, Baskerville Old Face, Times New Roman, serif; }\n"
            "            a        { color: rgb(100, 100, 100); transition: 0.75s; }\n"
            "            a:active { color: rgb(50, 50, 50); transition: 0.1s; }\n"
           )


def getDebugStyle():
    return ("            hr    { color: #EEE; }\n"
            "            table { margin: 30px; }\n"
            "            .system td { padding: 5px; border-bottom: dotted 1px #AAA; }\n"
           )


def getRawStyle():
    return ("            a      { text-decoration: none; }\n"
            "            table  { margin: 30px; }\n"
            "            td, th { padding: 10px 25px; }\n"
            "            thead  { color: #FFF; background: #555; }\n"
            "            td:nth-child(even) { text-align: right; }\n"
            "            tr:nth-child(even) { background: #EEE; }\n"
            "            .info  { text-align: center; }\n"
           )


def getPanelStyle():
    return ("            svg        { width: 100px;\n"
            "                         height: 100px;\n"
            "                         fill: rgb(160, 160, 160);\n"
            "                         transition: 0.75s;\n"
            "                       }\n"
            "            svg:active { fill: rgb(80, 80, 80); transition: 0.1s; }\n"
            "            .drive     { height: 400px; }\n"
            "            .simple    { height: 900px; }\n"
            "            .pro       { height: 1000px; }\n"
            "            .panel     { width: 600px;\n"
            "                         margin: auto;\n"
            "                         text-align: center;\n"
            "                       }\n"
           )


def getSimpleStyle():
    return ("            .links    { width: 350px;\n"
            "                        padding: 0px;\n"
            "                        margin: 100px auto;\n"
            "                        border-top: 0px;\n"
            "                        border: 1px solid #BBB;\n"
            "                        border-radius: 15px 15px 0px 0px;\n"
            "                        font-size: 20px;\n"
            "                        color: #888;\n"
            "                      }\n"
            "            .links li { list-style: none;\n"
            "                        background: #EEE;\n"
            "                        padding: 10px 20px;\n"
            "                        border-top: 1px solid #CCC;\n"
            "                      }\n"
            "            .links li:first-child { color: #FFF;\n"
            "                                    background: #555;\n"
            "                                    border: none;\n"
            "                                    border-radius: 10px 10px 0px 0px;\n"
            "                                  }\n"
           )



###########
## PANELS


def getLicensePanel():
    return ("        <h1>\n"
            "            The license of the μBot firmware\n"
            "        </h1>\n"
            "        This file is part of uBot_firmware.<br>\n"
            "        <a href='https://zza.hu/uBot_firmware' target='_blank'>https://zza.hu/uBot_firmware</a><br>\n"
            "        <a href='https://git.zza.hu/uBot_firmware' target='_blank'>https://git.zza.hu/uBot_firmware</a><br><br><br>\n"
            "        <h2>\n"
            "            MIT License\n"
            "        </h2>\n"
            "        Copyright (c) 2020-2021 Szabó László András <hu@zza.hu><br><br>\n"
            "        Permission is hereby granted, free of charge, to any person obtaining a copy<br>\n"
            "        of this software and associated documentation files (the \"Software\"), to deal<br>\n"
            "        in the Software without restriction, including without limitation the rights<br>\n"
            "        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell<br>\n"
            "        copies of the Software, and to permit persons to whom the Software is<br>\n"
            "        furnished to do so, subject to the following conditions:<br><br>\n"
            "        The above copyright notice and this permission notice shall be included in all<br>\n"
            "        copies or substantial portions of the Software.<br><br>\n"
            "        THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR<br>\n"
            "        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,<br>\n"
            "        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE<br>\n"
            "        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER<br>\n"
            "        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,<br>\n"
            "        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE<br>\n"
            "        SOFTWARE.<br>\n"
           )


def getDebugPanel():
    result = ("        <h3>Commands</h3>\n"
              "            {commands}\n"
              "        <br><br><hr><hr>\n"
              "        <h3>Program</h3>\n"
              "            {program}\n"
              "        <br><br><hr><hr>\n"
              "        <h3>System</h3>\n"
              "            <table class='system'>\n"
              "                <tr><td> <strong>Power on count:</strong> </td><td> {powerOnCount} </td><td>  </td></tr>\n"
              "                <tr><td> <strong>Saved programs:</strong> </td><td> {savedPrograms} </td><td>  </td></tr>\n"
              "                <tr><td> <strong>Firmware:</strong> </td><td> {firmware} </td><td><a href='license'>MIT License</a></td></tr>\n"
              "                <tr><td> <strong>Free memory:</strong> </td><td> {freeMemory}% </td><td> {memoryDetails} </td></tr>\n"
              "                <tr><td> <strong>Free space:</strong> </td><td> {freeSpace}% </td><td> {diskDetails} </td></tr>\n"
              "                <tr><td> <strong>System RTC:</strong> </td><td colspan='2'> {year}. {month:02d}. {day:02d}.&nbsp;&nbsp;&nbsp;{hour:02d} : {minute:02d} : {second:02d} </td></tr>\n"
              "            </table>\n"
             )

    firmware = config.get("system", "firmware")
    firmwareVersion = "{}.{}.{}".format(
        firmware[0], firmware[1], firmware[2]
    )

    allMem        = gc.mem_free() + gc.mem_alloc()
    freePercent   = gc.mem_free() * 100 // allMem
    memoryDetails = "{} / {}".format(gc.mem_free(), allMem)

    stat        = uos.statvfs("/")
    freeSpace   = stat[4] * stat[0] * 100 // (stat[2] * stat[1])       # f_bavail * f_bsize * 100 // f_blocks * f_frsize
    diskDetails = "{} / {}".format(stat[4] * stat[0], stat[2] * stat[1])
    dt = config.datetime()

    return result.format(
        commands = turtle._commandArray[:turtle._commandPointer].decode(),
        program  = turtle._programArray[:turtle._programParts[-1]].decode(),
        powerOnCount = config.get("system", "powerOnCount"),
        savedPrograms = len(uos.listdir("program/turtle")) + len(uos.listdir("program/json")),
        firmware = firmwareVersion,
        freeMemory = freePercent, memoryDetails = memoryDetails,
        freeSpace = freeSpace, diskDetails = diskDetails,
        year = dt[0], month = dt[1], day = dt[2],
        hour = dt[4], minute = dt[5], second = dt[6]
    )


def getDrivePanel():
    return ("        <table class = 'drive panel'>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(\"l\")' style='transform: rotate(-45deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(\"F\")'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(\"r\")' style='transform: rotate(45deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(\"L\")' style='transform: rotate(-90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(\"B\")' style='transform: rotate(180deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(\"R\")' style='transform: rotate(90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "        </table>\n"
           )


def getSimplePanel():
    return ("        <table class = 'simple panel'>\n"
            "            <tr>\n"
            "                <td></td>\n"
            "                <td><svg onclick='send(1)'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(128)' style='transform: rotate(-90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(64)'><use xlink:href='#play'></use></svg></td>\n"
            "                <td><svg onclick='send(16)' style='transform: rotate(90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td></td>\n"
            "                <td><svg onclick='send(32)' style='transform: rotate(180deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td colspan='3' style='height:100px;'></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(512)'><use xlink:href='#cross'></use></svg></td>\n"
            "                <td><svg onclick='send(2)'><use xlink:href='#pause'></use></svg></td>\n"
            "                <td><svg onclick='send(256)'><use xlink:href='#undo'></use></svg></td>\n"
            "            </tr>\n"
            "        </table>\n"
           )


def getProPanel():
    return ("        <table class = 'pro panel'>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(128)' style='transform: rotate(-45deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(1)'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(16)' style='transform: rotate(45deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(128)' style='transform: rotate(-90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(64)'><use xlink:href='#play'></use></svg></td>\n"
            "                <td><svg onclick='send(16)' style='transform: rotate(90deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(2)'><use xlink:href='#pause'></use></svg></td>\n"
            "                <td><svg onclick='send(32)' style='transform: rotate(180deg);'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg onclick='send(4)'><use xlink:href='#repeat'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(512)'><use xlink:href='#cross'></use></svg></td>\n"
            "                <td><svg onclick='send(256)'><use xlink:href='#undo'></use></svg></td>\n"
            "                <td><svg onclick='send(8)' style='transform: rotate(45deg);'><use xlink:href='#cross'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg onclick='send(6)' ><use xlink:href='#F1'></use></svg></td>\n"
            "                <td><svg onclick='send(10)'><use xlink:href='#F2'></use></svg></td>\n"
            "                <td><svg onclick='send(12)'><use xlink:href='#F3'></use></svg></td>\n"
            "            </tr>\n"
            "        </table>\n"
           )


def getSettingsPanel():
    return ("        <ul class='links'>\n"
            "            <li>Settings</li>\n"
            "            <li><a href='_datetime'>Date & Time</a></li>\n"
            "            <li><a href='_webrepl'>WebREPL</a></li>\n"
            "            <li><a href='_calibration'>Calibration</a></li>\n"
            "        </ul>\n"
            )


def getDateTimePanel():
    dt = config.datetime()
    return ("        <ul class='links'>\n"
            "            <li>Date & Time</li>\n"
            "            <li><table style='width: 100%; text-align: center;'><tr><td>{}. {:02d}. {:02d}.</td><td>{:02d} : {:02d} : {:02d}</td></tr></table></li>\n"
            "            <li><center><input type='date' id='date'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='time' id='time'></center></li>\n"
            "            <li><a href='_datetime' onclick='send(1)'>Save</a></li>\n"
            "            <li><a href='_settings'>Back to settings</a></li>\n"
            "        </ul>\n"
            ).format(dt[0], dt[1], dt[2], dt[4], dt[5], dt[6])


def getWebReplPanel():
    if config.get("webRepl", "active"):
        str0 = ""
        str1 = "STOP"
        str2 = "Stop"
    else:
        str0 = "in"
        str1 = "START"
        str2 = "Start"

    return ("        <ul class='links'>\n"
            "            <li>WebREPL</li>\n"
            "            <li>This service is {}active.</li>\n"
            "            <li><a href='_webrepl' onclick='send(\"{} WEBREPL\")'>{} WebREPL</a></li>\n"
            "            <li><a href='_settings'>Back to settings</a></li>\n"
            "        </ul>\n"
            ).format(str0, str1, str2)


def getCalibrationPanel():
    mag = [(), ()]

    if mag[0] == ():
        mag[0] = ("-", "-", "-")
    else:
        mag[0] = tuple(round(v, 2) for v in mag[0])

    if mag[1] == ():
        mag[1] = ("-", "-", "-")
    else:
        mag[1] = tuple(round(v, 2) for v in mag[1])

    return ("        <ul class='links'>\n"
            "            <li>Calibration</li>\n"
            "            <li>Min. X: {}, Y: {}, Z: {}</li>\n"
            "            <li>Max. X: {}, Y: {}, Z: {}</li>\n"
            "            <li><a href='_calibration' onclick='send(\"CALIBRATE FEEDBACK\")'>Calibrate feedback</a></li>\n"
            "            <li><a href='_settings'>Back to settings</a></li>\n"
            "        </ul>\n"
            ).format(mag[0][0], mag[0][1], mag[0][2], mag[1][0], mag[1][1], mag[1][2])


_sender =  ("\n"
            "        <script>\n"
            "            function send(value) {{\n"
            "                let object = {{\n"
            "                   \"title\" : \"{title}\",\n"
            "                   \"logging\" : {logging},\n"
            "                   {body}"
            "                }}\n\n"
            "                let json = JSON.stringify(object);\n\n"
            "                let xhr = new XMLHttpRequest();\n"
            "                xhr.open('POST', '', false);\n"
            "                xhr.setRequestHeader('Content-Type', 'application/json');\n"
            "                xhr.send(json);\n"
            "            }}\n"
            "        </script>\n")


def getTurtleMoveSender():
    return _sender.format(title = "Immediate command | μBot Drive", logging = "false", body = "\"command\" : [ \"STEP \" + value ]\n")


def getButtonPressSender():
    return _sender.format(title = "Pressed button | μBot Command", logging = "false", body = "\"command\" : [ \"PRESS \" + value ]\n")


def getServiceRequestSender():
    return _sender.format(title = "Service request | μBot Settings", logging = "true", body = "\"service\" : [ value ]\n")


def getDateTimeSender():
    getters = "document.getElementById(\"date\").value, document.getElementById(\"time\").value"
    return _sender.format(title = "DateTime setting | μBot Settings", body = "\"dateTime\" : [ {} ]\n".format(getters))



###########
## SVG

def getSvgDefinitionHead():
    return ("         <svg style='display:none' xmlns='http://www.w3.org/2000/svg'>\n"
            "             <defs>\n"
           )


def getSvgDefinitionFooter():
    return ("             </defs>\n"
            "         </svg>\n"
           )


def getArrowSymbol():
    return ("                 <symbol id='arrow' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268M206.763 43l95.446 135.667 10.371 14.592c1.543 2.028 1.584 2.221.403 1.891-.724-.203-3.716-.86-6.65-1.46L292 190.68l-19-4.004-17.624-3.807c-19.111-4.32-19.446-3.756-15.703 26.464l1.671 15.334 10.049 96.666L253.678 344l1.395 14.833.453 4.5H149.163l.388-2.5c.213-1.375.572-4.9.797-7.833s1.275-13.433 2.332-23.333l6.637-64c9.227-87.743 8.536-79.775 7.106-81.956-1.503-2.296-4.03-3.218-7.393-2.7-3.009.464-31.455 6.057-56.293 11.069-8.945 1.805-16.36 3.186-16.478 3.068s4.733-6.949 10.779-15.181l17.144-23.377L150.686 107l16.894-23 17.691-24 13.562-18.506c1.882-2.662 3.616-4.612 3.855-4.334s2.073 2.907 4.075 5.84' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getPlaySymbol():
    return ("                 <symbol id='play' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m-96.582 98.648c4.824 2.444 8.807 6.698 10.495 11.21l1.42 3.796v165.426l-2.012 4.216c-7.804 16.352-30.585 16.235-38.751-.199l-1.57-3.159-.175-82.303c-.194-91.568-.433-86.417 4.305-92.873 5.593-7.623 17.738-10.447 26.288-6.114m69.817-1.738c1.225.351 9.323 4.521 17.996 9.266L293 172.654c33.458 18.102 45.814 25.041 46.341 26.027 1.144 2.137-1.097 3.596-27.674 18.021l-45 24.467L229 261.677l-43.333 23.665c-29.478 16.148-32.836 16.993-36.828 9.26-1.642-3.181-.837-189.425.828-191.29 2.589-2.902 6.174-3.838 10.235-2.673' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getPauseSymbol():
    return ("                 <symbol id='pause' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C42.351 18.926-37.288 168.254 25.297 290.411c64.763 126.409 240.57 144.003 328.976 32.922C449.499 203.682 377.904 26.005 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m-21.248 98.648c4.823 2.444 8.806 6.698 10.494 11.21l1.42 3.796V281.95l-1.436 3.838c-6.472 17.298-30.926 17.944-39.327 1.038l-1.57-3.159-.174-82.303c-.195-91.568-.433-86.417 4.304-92.873 5.593-7.623 17.738-10.447 26.289-6.114m88.666 0c4.824 2.444 8.807 6.698 10.495 11.21l1.42 3.796V281.95l-1.436 3.838c-6.472 17.298-30.926 17.944-39.327 1.038l-1.57-3.159-.175-82.303c-.194-91.568-.433-86.417 4.305-92.873 5.593-7.623 17.738-10.447 26.288-6.114' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getRepeatSymbol():
    return ("                 <symbol id='repeat' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C42.351 18.926-37.288 168.254 25.297 290.411c64.763 126.409 240.57 144.003 328.976 32.922C449.499 203.682 377.904 26.005 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m22.666 54.955c30.175 2.282 61.008 15.115 82.496 34.335l4.278 3.826 3.113-2.973 12.978-12.589c12.258-11.95 14.367-12.965 20.83-10.03 7.394 3.359 7.049.71 6.827 52.466l-.188 44.052-1.923 2.52c-3.967 5.201-2.068 5.011-50.265 5.028-49.863.017-48.242.236-51.559-6.986-3.168-6.901-2.693-7.735 13.904-24.426l13.683-13.759-4.77-3.907c-36.857-30.192-91.035-27.418-124.759 6.388-52.581 52.71-25.518 142.429 47.475 157.388 45.254 9.274 92.35-17.596 106.482-60.753 2.474-7.555.284-6.902 23.927-7.124l20.638-.194 2.165 1.821c2.881 2.425 2.582 5.858-1.614 18.566-42.732 129.419-225.19 127.598-267.249-2.666C38.714 155.77 100.51 65.049 189.061 58.713c10.712-.766 10.53-.766 20.272-.029' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getF1Symbol():
    return ("                 <symbol id='F1' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C42.351 18.926-37.288 168.254 25.297 290.411c64.763 126.409 240.57 144.003 328.976 32.922C449.499 203.682 377.904 26.005 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m22.308 84.896c.212.344-1.321 9.777-3.407 20.961l-3.793 20.335-2.599.439c-3.256.55-2.412 2.366-6.99-15.027l-3.948-15-59.571-.347v74.877l22.062-.351c25.997-.414 23.063.851 26.875-11.585l2.838-9.26 6.558-.392-.211 53.725h-6.4l-2.913-9.667c-3.851-12.779-.809-11.432-26.747-11.845l-22.062-.351v36.384c0 42.339-1.186 37.426 9.848 40.818l9.485 2.917c1.377.425 1.702.997 1.872 3.296l.205 2.781H83.394l-.447-2.383c-.581-3.093-.68-3.028 9.053-5.912 4.583-1.358 8.783-2.908 9.333-3.444 1.086-1.058 1.579-153.87.509-157.676-.551-1.959-.968-2.158-11.509-5.492L83 94.106l-.41-5.431 48.205-.175 62.999-.338c8.684-.095 14.954.096 15.181.463m62.615 62.042c-1.754 53.311-1.983 72.266-1.151 95.243.535 14.778-.4 13.524 12.561 16.848 11.092 2.846 12.333 3.52 12.333 6.703v1.872h-74l-.111-1.666-.166-2.792c-.045-.909 2.101-1.665 11.195-3.942 6.188-1.549 11.738-3.304 12.334-3.9 1.034-1.036 1.741-92.929.722-93.948-.169-.169-5.557-.802-11.974-1.406-15.313-1.443-14.522-1.23-15.05-4.049-.598-3.187-1.34-2.904 14.215-5.406L257 150.072c13.835-2.5 14.691-2.465 14.59.595' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getF2Symbol():
    return ("                 <symbol id='F2' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C42.351 18.926-37.288 168.254 25.297 290.411c64.763 126.409 240.57 144.003 328.976 32.922C449.499 203.682 377.904 26.005 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m22.308 84.896c.212.344-1.321 9.777-3.407 20.961l-3.793 20.335-2.599.439c-3.256.55-2.412 2.366-6.99-15.027l-3.948-15-59.571-.347v74.877l22.062-.351c25.997-.414 23.063.851 26.875-11.585l2.838-9.26 6.558-.392-.211 53.725h-6.4l-2.913-9.667c-3.851-12.779-.809-11.432-26.747-11.845l-22.062-.351v36.384c0 42.339-1.186 37.426 9.848 40.818l9.485 2.917c1.377.425 1.702.997 1.872 3.296l.205 2.781H83.394l-.447-2.383c-.581-3.093-.68-3.028 9.053-5.912 4.583-1.358 8.783-2.908 9.333-3.444 1.086-1.058 1.579-153.87.509-157.676-.551-1.959-.968-2.158-11.509-5.492L83 94.106l-.41-5.431 48.205-.175 62.999-.338c8.684-.095 14.954.096 15.181.463m82.692 60.03C309.243 154.297 318 164.844 318 180.371c0 21.99-14.449 38.522-56.544 64.695L251.911 251l32.172.173c17.694.095 32.389-.055 32.656-.333s2.648-5.222 5.293-10.985l4.809-10.478 2.746-.556c1.658-.336 2.847-.307 3 .073.294.728-1.844 38.69-2.305 40.939l-.307 1.5H224.06l-.331-2.166c-.182-1.192-.457-3.571-.61-5.287l-.278-3.12 9.746-6.475c45-29.894 60.332-47.372 58.525-66.717-1.987-21.279-27.017-29.591-53.992-17.929-6.168 2.667-5.717 2.773-8.39-1.962-2.649-4.695-2.792-4.258 2.437-7.455 20.118-12.299 43.995-16.864 60.5-11.567' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getF3Symbol():
    return ("                 <symbol id='F3' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C42.351 18.926-37.288 168.254 25.297 290.411c64.763 126.409 240.57 144.003 328.976 32.922C449.499 203.682 377.904 26.005 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m22.308 84.896c.212.344-1.321 9.777-3.407 20.961l-3.793 20.335-2.599.439c-3.256.55-2.412 2.366-6.99-15.027l-3.948-15-59.571-.347v74.877l22.062-.351c25.997-.414 23.063.851 26.875-11.585l2.838-9.26 6.558-.392-.211 53.725h-6.4l-2.913-9.667c-3.851-12.779-.809-11.432-26.747-11.845l-22.062-.351v36.384c0 42.339-1.186 37.426 9.848 40.818l9.485 2.917c1.377.425 1.702.997 1.872 3.296l.205 2.781H83.394l-.447-2.383c-.581-3.093-.68-3.028 9.053-5.912 4.583-1.358 8.783-2.908 9.333-3.444 1.086-1.058 1.579-153.87.509-157.676-.551-1.959-.968-2.158-11.509-5.492L83 94.106l-.41-5.431 48.205-.175 62.999-.338c8.684-.095 14.954.096 15.181.463m79.358 59.98c20.172 5.348 31.334 17.231 31.334 33.36 0 18.576-11.8 31.849-36.834 41.433-5.362 2.053-5.255 2.32 1.13 2.813 30.845 2.378 49.514 24.827 42.725 51.374-7.693 30.079-45.363 49.691-101.415 52.799-9.501.527-8.852.88-9.617-5.236l-.465-3.727 2.238-.35c1.231-.193 4.338-.529 6.904-.748 47.024-4.01 75.779-22.943 75.921-49.99.126-24.09-18.914-37.392-49.185-34.361-4.423.443-8.235.925-8.471 1.07-.524.324-1.247-3.814-1.257-7.196-.009-2.775-.401-2.578 7.659-3.842 32.198-5.049 49.594-24.331 41.491-45.987-6.763-18.076-36.978-22.47-63.392-9.22-2.145 1.076-3.976 1.862-4.069 1.747-1.037-1.296-5.03-8.05-5.03-8.509 0-1.735 17.53-10.544 26.667-13.401 13.817-4.319 31.864-5.158 43.666-2.029' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getUndoSymbol():
    return ("                 <symbol id='undo' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m-4 35.533c6.343 2.637 6.277 2.283 6.549 34.691.131 15.609.436 28.565.678 28.792s4.939 1.043 10.439 1.816C296.116 118.016 358.36 210.711 334.256 304c-3.723 14.408-16.009 42.999-16.315 37.967-4.137-68.016-58.592-125.536-124.108-131.093l-4.5-.382-.079 22.254c-.111 31.45-.26 34.494-1.783 36.552-2.999 4.051-8.055 5.741-12.261 4.099-3.278-1.28-117.691-96.377-130.651-108.594-8.565-8.074-7.708-10.841 7.338-23.697L168.156 44.12c7.622-6.191 9.662-6.874 14.511-4.858' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )


def getCrossSymbol():
    return ("                 <symbol id='cross' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268M98.801 69.416c7.832 1.662 7.598 1.454 55.532 49.305l45.334 45.254L245 118.724c48.521-48.433 47.751-47.755 56.202-49.418 15.906-3.129 31.829 12.712 28.805 28.658-1.506 7.941-.51 6.816-49.192 55.534l-45.797 45.831 45.422 45.502c44.718 44.796 46.903 47.177 48.776 53.169 6.376 20.394-15.611 39.146-34.758 29.645-2.743-1.361-12.831-11.08-48.793-47.014l-45.998-45.298c-.365 0-21.064 20.384-45.999 45.298-48.345 48.307-47.817 47.84-55.992 49.482C80.918 333.478 64.872 314.78 70.118 298c1.873-5.992 4.057-8.373 48.775-53.169l45.422-45.502-45.797-45.831c-48.682-48.718-47.686-47.593-49.191-55.534-3.098-16.334 13.099-32.022 29.474-28.548' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
           )



############
## CATALOGS

title = {
    "/_settings"    : "&microBot Settings",
    "/_datetime"    : "&microBot Date & Time",
    "/_webrepl"     : "&microBot WebREPL",
    "/_calibration" : "&microBot Calibration",
    "/debug"        : "&microBot Debug",
    "/drive"        : "&microBot Drive",
    "/license"      : "&microBot MIT License",
    "/simple"       : "&microBot Simple",
    "/pro"          : "&microBot Professional"
}

style = {
    "/_settings"    : (getGeneralStyle, getSimpleStyle),
    "/_datetime"    : (getGeneralStyle, getSimpleStyle),
    "/_webrepl"     : (getGeneralStyle, getSimpleStyle),
    "/_calibration" : (getGeneralStyle, getSimpleStyle),
    "/debug"        : (getGeneralStyle, getDebugStyle),
    "/drive"        : (getGeneralStyle, getPanelStyle),
    "/license"      : (getGeneralStyle,),
    "/simple"       : (getGeneralStyle, getPanelStyle),
    "/pro"          : (getGeneralStyle, getPanelStyle)
}

parts = {
    "/_settings"    : (getSettingsPanel, getServiceRequestSender),
    "/_datetime"    : (getDateTimePanel, getDateTimeSender),
    "/_webrepl"     : (getWebReplPanel, getServiceRequestSender),
    "/_calibration" : (getCalibrationPanel, getServiceRequestSender),
    "/debug"        : (getDebugPanel,),

    "/drive"        : (getSvgDefinitionHead, getArrowSymbol, getSvgDefinitionFooter, getDrivePanel, getTurtleMoveSender),

    "/license"      : (getLicensePanel,),

    "/simple"       : (getSvgDefinitionHead, getArrowSymbol, getPlaySymbol, getPauseSymbol, getUndoSymbol, getCrossSymbol,
                       getSvgDefinitionFooter, getSimplePanel, getButtonPressSender
                      ),

    "/pro"          : (getSvgDefinitionHead, getArrowSymbol, getPlaySymbol, getPauseSymbol, getRepeatSymbol,
                       getF1Symbol, getF2Symbol, getF3Symbol, getUndoSymbol, getCrossSymbol, getSvgDefinitionFooter,
                       getProPanel, getButtonPressSender
                      )
}

title["/"] = title["/simple"]
style["/"] = style["/simple"]
parts["/"] = parts["/simple"]

title["/professional"] = title["/pro"]
style["/professional"] = style["/pro"]
parts["/professional"] = parts["/pro"]
