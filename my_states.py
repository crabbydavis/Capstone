# my_states.py

from state import State
import time
import wx
from wx.lib.pubsub import pub
import RPi.GPIO as GPIO 

ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = wx.NullColour

#gpio pins
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
# Setup the #gpio pins
GPIO.setup(ACTUATOR_RET, GPIO.OUT)
GPIO.setup(ACTUATOR_EXT, GPIO.OUT)
#gpio.setup(CHOC_PUMP_1, #gpio.OUT)
#gpio.setup(FILLIG_EXT, #gpio.OUT)
#gpio.setup(FILLING_RET, #gpio.OUT)
#gpio.setup(CHOC_PUMP_2, #gpio.OUT)

GPIO.output(ACTUATOR_RET, GPIO.HIGH)
GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
#gpio.output(CHOC_PUMP_1, #gpio.HIGH)
#gpio.output(FILLIG_EXT, #gpio.HIGH)
#gpio.output(FILLING_RET, #gpio.HIGH)
#gpio.output(CHOC_PUMP_2, #gpio.HIGH)

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
    #gpio.output(CHOC_PUMP_1, #gpio.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    #gpio.output(CHOC_PUMP_1, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = INACTIVE_COLOR)
    #time.sleep(sleep_time)

def runFilling():
    print("runFilling")
    fillingRunTime = .5
    cutTime = .2
    #sleep_time = STAGE_TIME - fillingRunTime - cutTime * 2
    #gpio.output(FILLIG_EXT, #gpio.LOW)
    extendExtruder()
    extendWire()
    retractWire()

def extendExtruder():
    print("In extendExtruder")
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_EXTRUDER", color = ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_EXTRUDER", color = INACTIVE_COLOR)

def retractExtruder():
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_EXTRUDER", color = ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_EXTRUDER", color = INACTIVE_COLOR)

def extendWire():
    print("In extendWire")
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_WIRE", color = ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_WIRE", color = INACTIVE_COLOR)

def retractWire():
    print("In retractWire")
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_WIRE", color = ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_WIRE", color = INACTIVE_COLOR)

def runChocPump2():
    print("runChocPump2")
    runTime = 5
    #sleep_time = STAGE_TIME - runTime
    #gpio.output(CHOC_PUMP_2, #gpio.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    #gpio.output(CHOC_PUMP_2, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = INACTIVE_COLOR)
    #time.sleep(sleep_time)

def extendActuator():
    print("extendActuator")
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
