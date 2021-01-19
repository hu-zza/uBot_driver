import sys

from machine import Pin, Timer
from utime   import sleep_ms

import ubot_buzzer as buzzer
import ubot_motor  as motor


_clockPin          = 0           # [need config()] Advances the decade counter (U3).
_inputPin          = 0           # [need config()] Checks the returning signal from turtle HAT.
_counterPosition   = 0           #                 The position of the decade counter (U3).
_pressLength       = 0           # [need config()]
_maxError          = 0           # [need config()]

_lastPressed       = [0, 0]      #                 Inside: [last pressed button, elapsed (button check) cycles]
_firstRepeat       = 0           # [need config()]
_loopChecking      = 0           # [need config()]
_moveLength        = 0           #
_turnLength        = 0           #
_breathLength      = 0           #

_endSignal         = ""          # [need config()] Sound indicates the end of program execution: buzzer.keyBeep(_endSignal)

_pressedListIndex  = 0
_pressedList       = 0           # [need config()] Low-level:  The last N (_pressLength + _maxError) buttoncheck results.
_commandArray      = bytearray() #                 High-level: Abstract commands, result of processed button presses.
_commandPointer    = 0           #                 Pointer for _commandArray.
_programArray      = bytearray() #                 High-level: Result of one or more added _commandArray.
_programPointer    = 0           #                 Pointer for _programArray.
_programParts      = []          #                 Positions by which _programArray can be split into _commandArray(s).

_loopCounter       = 0           #

_functionPosition  = [-1, -1, -1]                  # -1 : not defined, -0.1 : under definition, 0+ : defined
                                                   # If defined, this index refer to the first command of the function,
                                                   # instead of its curly brace "{".

_blockStartIndex   = 0           #
_blockPrevStarts   = []          #
_currentMapping    = 0           #
_previousMappings  = []          #
_runningProgram    = False       #
_timer             = Timer(-1)   #                 Executes the repeated button checks.

_blockBoundaries   = ((40, 41), (123, 125), (126, 126)) # (("(", ")"), ("{", "}"), ("~", "~"))

################################
## CONFIG

def config(config):
    global _clockPin
    global _inputPin
    global _pressLength
    global _maxError
    global _firstRepeat
    global _loopChecking
    global _moveLength
    global _turnLength
    global _breathLength
    global _endSignal
    global _pressedList
    global _currentMapping

    _clockPin = Pin(config.get("turtleClockPin"), Pin.OUT)
    _clockPin.off()

    _inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: _inputPin = Pin(16, Pin.IN)
    _inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
    _inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

    _pressLength  = config.get("turtlePressLength")
    _maxError     = config.get("turtleMaxError")
    _firstRepeat  = config.get("turtleFirstRepeat")
    _loopChecking = config.get("turtleLoopChecking")

    _moveLength   = config.get("turtleMoveLength")
    _turnLength   = config.get("turtleTurnLength")
    _breathLength = config.get("turtleBreathLength")

    _endSignal    = config.get("turtleEndSignal")

    _pressedList  = [0] * (_pressLength + _maxError)

    _currentMapping = _defaultMapping

    _timer.init(
        period = config.get("turtleCheckPeriod"),
        mode = Timer.PERIODIC,
        callback = lambda t:_addCommand(_getValidatedPressedButton())
    )



################################
## PUBLIC METHODS

def move(direction):
    if isinstance(direction, str):
        direction = ord(direction)

    if direction == 70:                 # "F" - FORWARD
        motor.move(1, _moveLength)
    elif direction == 66:               # "B" - BACKWARD
        motor.move(4, _moveLength)
    elif direction == 76:               # "L" - LEFT (90°)
        motor.move(2, _turnLength)
    elif direction == 108:              # "l" - LEFT (45°)
        motor.move(2, _turnLength // 2) #                       Placeholder...
    elif direction == 82:               # "R" - RIGHT (90°)
        motor.move(3, _turnLength)
    elif direction == 114:              # "r" - RIGHT (45°)
        motor.move(3, _turnLength // 2) #                       Placeholder...
    elif direction == 80:               # "P" - PAUSE
        motor.move(0, _moveLength)

    motor.move(0, _breathLength)        # Pause between movements.


def press(pressed):                     # pressed = 1<<buttonOrdinal
    if isinstance(pressed, str):
        pressed = int(pressed)

    _logLastPressed(pressed)
    _addCommand(pressed)



################################################################
################################################################
##########
##########  PRIVATE, CLASS-LEVEL METHODS
##########


################################
## BUTTON PRESS PROCESSING

def _getValidatedPressedButton():
    global _lastPressed

    pressed = _getPressedButton()

    _logLastPressed(pressed)

    if _lastPressed[1] == 1 or _firstRepeat < _lastPressed[1]:    # Lack of pressing returns same like a button press.
        _lastPressed[1] = 1                                       # In this case the returning value is 0.
        return pressed
    else:
        return 0                                                 # If validation is in progress, returns 0.


def _logLastPressed(pressed):
    global _lastPressed
    if pressed == _lastPressed[0]:
        _lastPressed[1] += 1
    else:
        _lastPressed = [pressed, 1]


def _getPressedButton():
    global _pressedList
    global _pressedListIndex

    pressed = 0

    for i in range(10):
        # pseudo pull-down                 # DEPRECATED: New PCB design (2.1) will resolve this.
        if _inputPin.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

        if _inputPin.value() == 1:
            pressed += 1<<_counterPosition # pow(2, _counterPosition)

        _advanceCounter()

    # shift counter's "resting position" to the closest pressed button to eliminate BTN LED flashing
    if 0 < pressed:
        while bin(1024 + pressed)[12 - _counterPosition] != "1":
            _advanceCounter()

    _pressedList[_pressedListIndex] = pressed
    _pressedListIndex += 1
    if len(_pressedList) <= _pressedListIndex:
            _pressedListIndex = 0

    errorCount = 0

    for i in range(len(_pressedList)):
        count = _pressedList.count(_pressedList[i])

        if _pressLength <= count:
            return _pressedList[i]

        errorCount += count
        if _maxError < errorCount:
            return 0


def _advanceCounter():
    global _counterPosition

    _clockPin.on()

    if 9 <= _counterPosition:
        _counterPosition = 0
    else:
        _counterPosition += 1

    _clockPin.off()



################################
## BUTTON PRESS INTERPRETATION

def _addCommand(pressed):
    try:
        if pressed == 0:                # result = 0 means, there is nothing to save to _commandArray.
            result = 0                  # Not only lack of buttonpress (pressed == 0) returns 0.
        elif _runningProgram:
            result = _startOrStop(())   # Stop program execution.
        else:
            tupleWithCallable = _currentMapping.get(pressed)                # Dictionary based switch...case

            if tupleWithCallable == None:                                   # Default branch
                result = 0
            else:
                if tupleWithCallable[1] == ():
                    result = tupleWithCallable[0]()
                else:
                    result = tupleWithCallable[0](tupleWithCallable[1])

        if result != 0:
            if isinstance(result, int):
                _addToCommandArray(result)
            elif isinstance(result, tuple):
                for r in result:
                    _addToCommandArray(r)
            else:
                print("Wrong result: {}".format(result))
    except Exception as e:
        sys.print_exception(e)


def _addToCommandArray(command):
    global _commandArray
    global _commandPointer

    if _commandPointer < len(_commandArray):
        _commandArray[_commandPointer] = command
    else:
        _commandArray.append(command)

    _commandPointer += 1



################################
## HELPER METHODS FOR BLOCKS

def _blockStarted(newMapping):
    global _blockStartIndex
    global _currentMapping

    _blockPrevStarts.append(_blockStartIndex)
    _blockStartIndex = _commandPointer
    _previousMappings.append(_currentMapping)
    _currentMapping  = newMapping
    buzzer.setDefaultState(1)
    buzzer.keyBeep("beepStarted")


def _blockCompleted(deleteFlag):
    global _commandPointer
    global _blockStartIndex
    global _currentMapping

    if len(_previousMappings) != 0:
        if deleteFlag:
            _commandPointer = _blockStartIndex

        _blockStartIndex = _blockPrevStarts.pop()
        _currentMapping  = _previousMappings.pop()

        if len(_previousMappings) == 0:             # len(_previousMappings) == 0 means all blocks are closed.
            buzzer.setDefaultState(0)

        if deleteFlag:
            buzzer.keyBeep("beepDeleted")
            return True
        else:
            buzzer.keyBeep("beepCompleted")
            return False


def _getOppositeBoundary(commandPointer):
    bondary = _commandArray[commandPointer]

    for bondaryPair in _blockBoundaries:
        if bondary == bondaryPair[0]:
            return bondaryPair[1]
        elif bondary == bondaryPair[1]:
            return bondaryPair[0]
    return -1


def _isTagBoundary(commandPointer):
    return _commandArray[commandPointer] == _getOppositeBoundary(commandPointer)



################################
## STANDARDIZED FUNCTIONS

def _startOrStop(arguments):                # (blockLevel,)
    global _runningProgram

    buzzer.keyBeep("beepProcessed")
    _runningProgram = not _runningProgram

    _toPlay  = _programArray[:] + _commandArray[:_commandPointer]

    _pointerStack = []
    _pointer      = 0 if len(_commandArray) == 0 else len(_programArray)
    _counterStack = []

    if arguments[0] == True:                # Block-level
        _pointer += _blockStartIndex + 1    # + 1 is necessary to begin at the real command.

    if _runningProgram and _endSignal != "":
        motor.setCallback((lambda: buzzer.keyBeep(_endSignal), True))


    while _runningProgram:
        remaining = len(_toPlay) - 1 - _pointer #      Remaining bytes in _toPlay bytearray. 0 if _toPlay[_pointer] == _toPlay[-1]
        checkCounter = False


        if remaining < 0:                       #      If everything is executed, exits.
            _runningProgram = False


        elif _toPlay[_pointer] == 40:           # "("

            _pointerStack.append(_pointer)      #      Save the position of the loop's starting parentheses: "("

            while _pointer < len(_toPlay) and _toPlay[_pointer] != 42: # "*"  Jump to the end of the loop's body.
                _pointer += 1

            remaining = len(_toPlay) - 1 - _pointer

            if 1 <= remaining and _toPlay[_pointer] == 42:
                _counterStack.append(_toPlay[_pointer + 1] - 48) # Counter was increased at definition by 48. b'0' == 48
                checkCounter = True
            else:
                _runningProgram = False


        elif _toPlay[_pointer] == 42:           # "*"  End of the body of the loop.
            _counterStack[-1] -= 1              #      Decrease the loop counter.
            checkCounter = True


        elif _toPlay[_pointer] == 123:          # "{"  Start of a function.

            while _pointer < len(_toPlay) and _toPlay[_pointer] != 125: # "}" Jump to the function's closing curly brace.
                _pointer += 1

            if _toPlay[_pointer] != 125:        #      Means the _pointer < len(_toPlay) breaks the while loop.
                _runningProgram = False


        elif _toPlay[_pointer] == 124:          # "|"  End of the currently executed function.
            _pointer = _pointerStack.pop()      #      Jump back to where the function call occurred.


        elif _toPlay[_pointer] == 126:          # "~"
            if 2 <= remaining and _toPlay[_pointer + 2] == 126: # Double-check: 1. Enough remaining to close function call; 2. "~"
                _pointerStack.append(_pointer + 2)              # Save the returning position as the second tilde: "~"
                _pointer = _functionPosition[_toPlay[_pointer + 1] - 49]    # not 48! functionId - 1 = array index
            else:                                               # Maybe it's an error, so stop execution.
                _runningProgram = False


        else:
            move(_toPlay[_pointer])             # Execute the command. If it fails, it's a short (_breathLength) rest.


        if checkCounter:
            if 0 < _counterStack[-1]:           #      If the loop counter is greater than 0.
                _pointer = _pointerStack[-1]    #      Jump back to the loop starting position.
            else:
                del _pointerStack[-1]           #      Delete the loop's starting position from stack.
                del _counterStack[-1]           #      Delete the loop's counter from stack.
                _pointer += 2                   #      Jump to the loop's closing parentheses: ")"

        _pointer += 1

    return 0


# COMMAND AND PROGRAM ARRAY

def _addToProgramArray():
    return 0


# LOOP

def _createLoop(arguments):                 # (creationState,)                40 [statements...] 42 [iteration count] 41
    global _currentMapping
    global _loopCounter

    if arguments[0] == 40:
        _blockStarted(_loopBeginMapping)
        _loopCounter = 0
        return 40
    elif arguments[0] == 42:
        if _commandPointer - _blockStartIndex < 2:      # If the body of the loop is empty,
            _blockCompleted(True)                       # close and delete the complete block.
            return 0
        else:
            _currentMapping = _loopCounterMapping
            buzzer.keyBeep("beepInputNeeded")
            return 42
    elif arguments[0] == 41:
         # _blockCompleted deletes the loop if counter is zero, and returns with the result of the
         # deletion (True if deleted). This returning value is used as index: False == 0, and True == 1
         # Increase _loopCounter by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
        return ((_loopCounter + 48, 41), 0)[_blockCompleted(_loopCounter == 0)]


def _modifyLoopCounter(arguments):          # (value,)     Increasing by this value, if value == 0, it resets he counter
    global _loopCounter

    if _loopCounter + arguments[0] < 0:     # Checks lower boundary.
        _loopCounter = 0
        buzzer.keyBeep("beepBoundary")
    elif 255 < _loopCounter + arguments[0]: # Checks upper boundary.
        _loopCounter = 255
        buzzer.keyBeep("beepBoundary")
    elif arguments[0] == 0:                 # Reset the counter. Use case: forget the exact count and press 'X'.
        _loopCounter = 0
        buzzer.keyBeep("beepDeleted")
    else:                                   # General modification.
        _loopCounter += arguments[0]
        buzzer.keyBeep("beepInAndDecrease")
    return 0


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 2 or (_loopChecking == 1 and _loopCounter <= 20):
        buzzer.keyBeep("beepAttention")
        buzzer.midiBeep(64, 100, 500, _loopCounter)
    else:
        buzzer.keyBeep("beepTooLong")
    buzzer.rest(1000)
    return 0


# FUNCTION

def _manageFunction(arguments):             # (functionId, onlyCall)                    123 [statements...] 124 [id] 125
    global _functionPosition                #                           function call:  126 [id] 126
    id = arguments[0]

    # Calling the function if it is defined, or flag 'only call' is True and it is not under definition.
    # In the second case, position -1 (undefined) is fine. (lazy initialization)
    if 0 <= _functionPosition[id - 1] or (arguments[1] and _functionPosition[id - 1] != -0.1):
        buzzer.keyBeep("beepProcessed")
        return (126, arguments[0] + 48, 126)          # Increase by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
    elif _functionPosition[id - 1] == -0.1:           # End of defining the function
        # Save index to _functionPosition, because _blockStartIndex will be destroyed during _blockCompleted().
        _functionPosition[id - 1] = len(_programArray) + _blockStartIndex

        # If function contains nothing
        # (_commandPointer - _blockStartIndex < 2 -> Function start and end are adjacent.),
        # delete it by _blockCompleted() which return a boolean (True if deleted).
        # If this returning value is True, retain len(_programArray) + _blockStartIndex, else overwrite it with -1.
        if _blockCompleted(_commandPointer - _blockStartIndex < 2):
            _functionPosition[id - 1] = -1

        return (0, (124, arguments[0] + 48, 125))[0 <= _functionPosition[id - 1]] # False == 0, and True == 1 (defined)

    else:                                             # Beginning of defining the function
        _blockStarted(_functionMapping)
        _functionPosition[id - 1] = -0.1              # In progress, so it isn't -1 (undefined) or 0+ (defined).
        return 123


# GENERAL

def _beepAndReturn(arguments):              # (keyOfBeep, returningValue)
    buzzer.keyBeep(arguments[0])
    return arguments[1]


def _undo(arguments):                       # (blockLevel,)
    global _commandPointer
    global _functionPosition

    # Sets the maximum range of undo in according to blockLevel flag.
    undoLowerBoundary = _blockStartIndex + 1 if arguments[0] else 0

    if undoLowerBoundary < _commandPointer:                         # If there is anything that can be undone.
        _commandPointer -= 1
        buzzer.keyBeep("beepUndone")

        # If toBeUndone is a block boundary, _getOppositeBoundary returns with its pair (the beginning of the block).
        boundary = _getOppositeBoundary(_commandPointer)

        if boundary != -1:
            if boundary == 123:                                    # If it undoes a function declaration.
                _functionPosition[_commandArray[_commandPointer - 1] - 49] = -1 # not 48! functionId - 1 = array index
            while True:                                            # General undo decreases the pointer by one, so this
                _commandPointer -= 1                               # do...while loop can handle identic boundary pairs.
                if _commandArray[_commandPointer] == boundary:
                    break

            if not _isTagBoundary(_commandPointer):                # Tags (like function calling) need no keyBeep().
                buzzer.keyBeep("beepDeleted")

        if _commandPointer == undoLowerBoundary:
            buzzer.keyBeep("beepBoundary")
    else:
        if arguments[0] or 0 == _programPointer:      # Block level undo or no more loadable command from _programArray.
            buzzer.keyBeep("beepBoundary")
        else:
            buzzer.keyBeep("beepLoaded")
            # Move last added _commandArray from _programArray to _commandArray variable, etc...
    return 0


def _delete(arguments):                     # (blockLevel,)
    global _commandPointer
    global _programPointer
    global _functionPosition

    if arguments[0] == True:                # Block-level
        _blockCompleted(True)               # buzzer.keyBeep("beepDeleted") is called inside _blockCompleted(True)
        for i in range(3):                  # Delete position of unfinished function, if there are any.
            if _functionPosition[i] == 0:
                _functionPosition[i] = -1
    else:                                   # Not block-level: the whole _commandArray is affected.
        buzzer.keyBeep("beepDeleted")
        if _commandPointer != 0:
            _commandPointer = 0
            # for .... if 124 X 125 -> _functionPosition[X] = -1
        else:
            _programPointer = 0
            _functionPosition = [-1, -1, -1]
            buzzer.keyBeep("beepBoundary")


    return 0


def _customMapping():
    buzzer.keyBeep("beepLoaded")
    return 0



################################
## MAPPINGS

_defaultMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, False)),                         # F1
    8:    (_addToProgramArray, ()),                                 # ADD
    10:   (_manageFunction,    (2, False)),                         # F2
    12:   (_manageFunction,    (3, False)),                         # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (False,)),                           # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
    256:  (_undo,              (False,)),                           # UNDO
    512:  (_delete,            (False,)),                           # DELETE
    1023: (_customMapping,     ())                                  # MAPPING
}


_loopBeginMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (42,)),                              # REPEAT (*)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (True,)),                            # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}


_loopCounterMapping = {
    1:    (_modifyLoopCounter, (1,)),                               # FORWARD
    4:    (_createLoop,        (41,)),                              # REPEAT (end)
    16:   (_modifyLoopCounter, (1,)),                               # RIGHT
    32:   (_modifyLoopCounter, (-1,)),                              # BACKWARD
    64:   (_checkLoopCounter,  ()),                                 # START / STOP
    128:  (_modifyLoopCounter, (-1,)),                              # LEFT
    512:  (_modifyLoopCounter, (0,))                                # DELETE
}


_functionMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (True,)),                            # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}
