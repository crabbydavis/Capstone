# my_states.py

from state import State
import time
import wx
from wx.lib.pubsub import pub
import RPi.GPIO as GPIO 

ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = wx.NullColour

# GPIO pins
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
CHOC_PUMP_2 = 32
FILLING_EXT = 26
FILLING_RET = 24
CUT_EXT = 22
CUT_RET = 18

# Costants for timing
chocPump1RunTime = 8
chocPump2RunTime = 10
actuatorTime = 10
stageTime = 30
runTime = 60

ranFirstWarmUp = False
ranSecondWarmUp = False
ranFirstCooldown = False
ranSecondCooldown = False

# Set numbering mode for the program
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# Setup the GPIO pins
GPIO.setup(ACTUATOR_RET, GPIO.OUT)
GPIO.setup(ACTUATOR_EXT, GPIO.OUT)
GPIO.setup(CHOC_PUMP_1, GPIO.OUT)
GPIO.setup(FILLING_EXT, GPIO.OUT)
GPIO.setup(FILLING_RET, GPIO.OUT)
GPIO.setup(CHOC_PUMP_2, GPIO.OUT)

GPIO.output(ACTUATOR_RET, GPIO.HIGH)
GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
GPIO.output(FILLING_EXT, GPIO.HIGH)
GPIO.output(FILLING_RET, GPIO.HIGH)
GPIO.output(CHOC_PUMP_2, GPIO.HIGH)

# Start of our states
class InitState(State):
    global ranFirstWarmUp
    global ranSecondWarmUp
    global ranFirstCooldown
    global ranSecodCooldown
    def on_event(self, event):
        if event == 'start':
            ranFirstWarmUp = False
            ranSecondWarmUp = False
            ranFirstCooldown = False
            ranSecodCooldown = False
            return FirstWarmUpState()
        return InitState()

# Start of our states
class FirstWarmUpState(State):
    def on_event(self, event):
        global ranFirstWarmUp
        print(stageTime)
        firstWarmUpStageTime = stageTime - chocPump1RunTime - actuatorTime
        extendActuator()
        retractActuator()
        runChocPump1()
        time.sleep(firstWarmUpStageTime)
        if ranFirstWarmUp == False:
            ranFirstWarmUp = True
            return FirstWarmUpState()
        else:
            return SecondWarmupState()

# Start of our states
class SecondWarmupState(State):
    def on_event(self, event):
        global ranSecondWarmUp
        print(stageTime)
        secondWarmUpStageTime = stageTime - chocPump1RunTime - actuatorTime
        extendActuator()
        retractActuator()
        runChocPump1()
        #runFilling()
        time.sleep(secondWarmUpStageTime)
        if ranSecondWarmUp == False:
            ranSecondWarmUp = True
            return SecondWarmupState()
        else:
            return RunState()

# Start of our states
class RunState(State):
    def on_event(self, event):
        runStageTime = runTime - chocPump1RunTime - chocPump2RunTime - actuatorTime
        if event == 'run':
            extendActuator()
            retractActuator()
            runChocPump1()
            #runFilling()
            runChocPump2()
            time.sleep(runStageTime)
            return RunState()
        elif event == 'finish':
            return FirstCooldownState()
        return self

# Start of our states
class FirstCooldownState(State):
    def on_event(self, event):
        global ranFirstCooldown
        firstCooldownStageTime = stageTime - chocPump2RunTime - actuatorTime
        extendActuator()
        retractActuator()
        #runFilling()
        runChocPump2()
        if ranFirstCooldown == False:
            ranFirstCooldown = True
            return FirstCooldownState()
        else:
            return SecondCooldownState()

# Start of our states
class SecondCooldownState(State):
    def on_event(self, event):
        global ranSecondCooldown
        secondCooldownStageTime = stageTime - chocPump2RunTime - actuatorTime
        extendActuator()
        retractActuator()
        runChocPump2()
        if ranSecondCooldown == False:
            ranSecondCooldown = True
            return SecondCooldownState()
        else:
            return StopState()


class StopState(State):

    def on_event(self, event):
        extendActuator()
        retractActuator()
        return self

#################################################################
# Functions for running the chocolate processes of the machine
#################################################################
def runChocPump1():
    print("runChocPump1")
    runTime = 8
    GPIO.output(CHOC_PUMP_1, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = INACTIVE_COLOR)

def runFilling():
    print("runFilling")
    fillingRunTime = .5
    cutTime = .2
    GPIO.output(FILLING_EXT, GPIO.LOW)
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
    runTime = 12
    GPIO.output(CHOC_PUMP_2, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = INACTIVE_COLOR)

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

# End of our states.
