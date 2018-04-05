# my_states.py

from state import State
import time
import wx
from wx.lib.pubsub import pub
import RPi.GPIO as GPIO 

ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = wx.NullColour

GPIO pins
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
FILLIG_EXT = 32
FILLING_RET = 26
CHOC_PUMP_2 = 24
CUT_EXT = 22
CUT_RET = 18

# Set numbering mode for the program
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# Setup the GPIO pins
GPIO.setup(ACTUATOR_RET, GPIO.OUT)
GPIO.setup(ACTUATOR_EXT, GPIO.OUT)
GPIO.setup(CHOC_PUMP_1, GPIO.OUT)
GPIO.setup(FILLIG_EXT, GPIO.OUT)
GPIO.setup(FILLING_RET, GPIO.OUT)
GPIO.setup(CHOC_PUMP_2, GPIO.OUT)

GPIO.output(ACTUATOR_RET, GPIO.HIGH)
GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
GPIO.output(FILLIG_EXT, GPIO.HIGH)
GPIO.output(FILLING_RET, GPIO.HIGH)
GPIO.output(CHOC_PUMP_2, GPIO.HIGH)

# Start of our states
class InitState(State):
    def on_event(self, event):
        if event == 'start':
            extendActuator()
            retractActuator()
            return FirstWarmUpState()
        return InitState()

# Start of our states
class FirstWarmUpState(State):
    def on_event(self, event):
        extendActuator()
        runChocPump1()
        retractActuator()
        return SecondWarmupState()

# Start of our states
class SecondWarmupState(State):
    def on_event(self, event):
        extendActuator()
        runChocPump1()
        runFilling()
        retractActuator()
        return RunState()

# Start of our states
class RunState(State):
    def on_event(self, event):
        print(event)
        if event == 'run':
            extendActuator()
            runChocPump1()
            runFilling()
            runChocPump2()
            retractActuator()
            return RunState()
        elif event == 'finish':
            return FirstCooldownState()
        return self

# Start of our states
class FirstCooldownState(State):
    def on_event(self, event):
        extendActuator()
        runFilling()
        runChocPump2()
        retractActuator()
        return SecondCooldownState()

# Start of our states
class SecondCooldownState(State):

    def on_event(self, event):
        extendActuator()
        runChocPump2()
        retractActuator()
        return StopState()


class StopState(State):

    def on_event(self, event):
        return self

#################################################################
# Functions for running the chocolate processes of the machine
#################################################################
def runChocPump1():
    print("runChocPump1")
    runTime = 5
    #sleep_time = STAGE_TIME - runTime
    GPIO.output(CHOC_PUMP_1, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = INACTIVE_COLOR)
    #time.sleep(sleep_time)

def runFilling():
    print("runFilling")
    fillingRunTime = .5
    cutTime = .2
    #sleep_time = STAGE_TIME - fillingRunTime - cutTime * 2
    GPIO.output(FILLIG_EXT, GPIO.LOW)
    extendExtruder()
    extendWire()
    retractWire()

def extendExtruder():
    print("In extendExtruder")
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_EXTRUDER", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_EXTRUDER", color = INACTIVE_COLOR)

def retractExtruder():
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_EXTRUDER", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_EXTRUDER", color = INACTIVE_COLOR)

def extendWire():
    print("In extendWire")
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_WIRE", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_WIRE", color = INACTIVE_COLOR)

def retractWire():
    print("In retractWire")
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_WIRE", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_WIRE", color = INACTIVE_COLOR)

def runChocPump2():
    print("runChocPump2")
    runTime = 5
    #sleep_time = STAGE_TIME - runTime
    GPIO.output(CHOC_PUMP_2, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = INACTIVE_COLOR)
    #time.sleep(sleep_time)

def extendActuator():
    GPIO.output(ACTUATOR_EXT, GPIO.LOW)
    # Tell the GUI about them
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = INACTIVE_COLOR)
    
def retractActuator():
    print("retractActuator")
    GPIO.output(ACTUATOR_RET, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = ACTIVE_COLOR)
    time.sleep(5)
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = INACTIVE_COLOR)
    time.sleep(2)

# End of our states.
