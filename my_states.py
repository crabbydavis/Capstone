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
#FILLING_EXT = 26
#FILLING_RET = 24
#CUT_EXT = 22
#CUT_RET = 18

# Costants for timing
chocPump1RunTime = 8
chocPump2RunTime = 10
actuatorTime = 5
actuatorTotalTime = 10
stageTime = 30
runTime = 60

ranFirstWarmUp = False
ranSecondWarmUp = False
ranFirstCooldown = False
ranSecondCooldown = False
shouldStop = False

# Set numbering mode for the program
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Setup the GPIO pins
GPIO.setup(ACTUATOR_RET, GPIO.OUT)
GPIO.setup(ACTUATOR_EXT, GPIO.OUT)
GPIO.setup(CHOC_PUMP_1, GPIO.OUT)
GPIO.setup(CHOC_PUMP_2, GPIO.OUT)
#GPIO.setup(FILLING_EXT, GPIO.OUT)
#GPIO.setup(FILLING_RET, GPIO.OUT)

GPIO.output(ACTUATOR_RET, GPIO.HIGH)
GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
#GPIO.output(FILLING_EXT, GPIO.HIGH)
#GPIO.output(FILLING_RET, GPIO.HIGH)

# Start of our states
class InitState(State):
    
    def on_event(self, event):
        global ranFirstWarmUp
        global ranSecondWarmUp
        global ranFirstCooldown
        global ranSecodCooldown
        global shouldStop

        pub.subscribe(emergencyStop(), "EMERGENCY_STOP")

        if event == 'start':
            ranFirstWarmUp = False
            ranSecondWarmUp = False
            ranFirstCooldown = False
            ranSecodCooldown = False
            shouldStop = False
            return FirstWarmUpState()
        return InitState()

# Start of our states
class FirstWarmUpState(State):
    def on_event(self, event):
        global ranFirstWarmUp
        global shouldStop

        if event == 'emergencyStop':
            return InitState()
        else:
            firstWarmUpStageTime = stageTime - chocPump1RunTime - actuatorTotalTime
            extendActuator()
            if shouldStop == True:
            	return InitState()
			retractActuator()
            if shouldStop == True:
            	return InitState()
            if shouldStop == True:
            	return InitState()
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
        global shouldStop

        if event == 'emergencyStop':
            return InitState()
        else:
            secondWarmUpStageTime = stageTime - chocPump1RunTime - actuatorTotalTime
            extendActuator()
            if shouldStop == True:
            	return InitState()
			retractActuator()
            if shouldStop == True:
				return InitState()
			runChocPump1()
            if shouldStop == True:
            	return InitState()
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
        global shouldStop
        runStageTime = runTime - chocPump1RunTime - chocPump2RunTime - actuatorTotalTime
        if event == 'run':
            extendActuator()
            if shouldStop == True:
				return InitState()
            retractActuator()
            if shouldStop == True:
				return InitState()
			runChocPump1()
            #runFilling()
            if shouldStop == True:
				return InitState()
			runChocPump2()
            if shouldStop == True:
				return InitState()
            time.sleep(runStageTime)
            return RunState()
        elif event == 'finish':
            return FirstCooldownState()
        elif event == 'emergencyStop':
            return InitState()
        return self

# Start of our states
class FirstCooldownState(State):
    def on_event(self, event):
        global ranFirstCooldown
        if event == 'emergencyStop':
            return InitState()
        else:
            firstCooldownStageTime = stageTime - chocPump2RunTime - actuatorTotalTime
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
        if event == 'emergencyStop':
            return InitState()
        else:
            secondCooldownStageTime = stageTime - chocPump2RunTime - actuatorTotalTime
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
        if event == 'emergencyStop':
            return InitState()
        else:
            extendActuator()
            retractActuator()
        return InitState()

#################################################################
# Functions for running the chocolate processes of the machine
#################################################################
def emergencyStop():
    global shouldStop
    shouldStop = True

def runChocPump1():
    print("runChocPump1")
    GPIO.output(CHOC_PUMP_1, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_1", color = ACTIVE_COLOR)
    time.sleep(chocPump1RunTime) # Number of seconds that the pi will sleep
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
    GPIO.output(CHOC_PUMP_2, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = ACTIVE_COLOR)
    time.sleep(chocPump2RunTime) # Number of seconds that the pi will sleep
    GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RUN_CHOC_PUMP_2", color = INACTIVE_COLOR)

def extendActuator():
    GPIO.output(ACTUATOR_EXT, GPIO.LOW)
    # Tell the GUI about them
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = ACTIVE_COLOR)
    time.sleep(actuatorTime)
    GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = INACTIVE_COLOR)
    
def retractActuator():
    print("retractActuator")
    GPIO.output(ACTUATOR_RET, GPIO.LOW)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = ACTIVE_COLOR)
    time.sleep(actuatorTime)
    GPIO.output(ACTUATOR_RET, GPIO.HIGH)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = INACTIVE_COLOR)

# End of our states.
