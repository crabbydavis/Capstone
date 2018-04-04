# my_states.py

from state import State
import time
import wx
from wx.lib.pubsub import pub


ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = wx.NullColour

# Start of our states
class InitState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        if event == 'start':
            extendActuator()
            retractActuator()
            return FirstWarmUpState()
        return InitState()

# Start of our states
class FirstWarmUpState(State):
    """
    The state which indicates that there are limited device capabilities.
    """
    def on_event(self, event):
        extendActuator()
        runChocPump1()
        retractActuator()
        return SecondWarmupState()

# Start of our states
class SecondWarmupState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        extendActuator()
        runChocPump1()
        runFilling()
        retractActuator()
        return RunState()

# Start of our states
class RunState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

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
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        extendActuator()
        runFilling()
        runChocPump2()
        retractActuator()
        return SecondCooldownState()

# Start of our states
class SecondCooldownState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        extendActuator()
        runChocPump2()
        retractActuator()
        return StopState()


class StopState(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

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
    #gpio.output(ACTUATOR_EXT, #gpio.LOW)
    #arg.extendActuator_button.SetBackgroundColour(ACTIVE_COLOR)
    # Tell the GUI about them
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    wx.CallAfter(pub.sendMessage, "EXTEND_ACTUATOR", color = INACTIVE_COLOR)
    
def retractActuator():
    print("retractActuator")
    #gpio.output(ACTUATOR_RET, #gpio.LOW)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = ACTIVE_COLOR)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    time.sleep(5)
    wx.CallAfter(pub.sendMessage, "RETRACT_ACTUATOR", color = INACTIVE_COLOR)


# End of our states.