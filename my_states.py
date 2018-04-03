# my_states.py

from state import State
import time
from wx.lib.pubsub import pub

ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = '#f7f7f7'

# Start of our states
class InitState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event, arg):
        if event == 'start':
            return FirstWarmUpState()
        return InitState()

# Start of our states
class FirstWarmUpState(State):
    """
    The state which indicates that there are limited device capabilities.
    """
    def on_event(self, event, mainObject):
        extendActuator(mainObject)
        runChocPump1(mainObject)
        retractActuator(mainObject)
        return SecondWarmupState()

# Start of our states
class SecondWarmupState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event, mainObject):
        extendActuator(mainObject)
        runChocPump1(mainObject)
        runFilling(mainObject)
        retractActuator(mainObject)
        return RunState()

# Start of our states
class RunState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event, mainObject):
        print(event)
        if event == 'run':
            extendActuator(mainObject)
            runChocPump1(mainObject)
            runFilling(mainObject)
            runChocPump2(mainObject)
            retractActuator(mainObject)
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
        extendActuator(self)
        runFilling(self)
        runChocPump2(self)
        retractActuator(self)
        return SecondCooldownState()

# Start of our states
class SecondCooldownState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        extendActuator(self)
        runChocPump2(self)
        retractActuator(self)
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
def runChocPump1(self):
    print("runChocPump1")
    runTime = .5
    #sleep_time = STAGE_TIME - runTime
    #gpio.output(CHOC_PUMP_1, #gpio.LOW)
    #self.runChocPump1_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    #gpio.output(CHOC_PUMP_1, #gpio.HIGH)
    #self.runChocPump1_button.SetBackgroundColour(INACTIVE_COLOR)
    #time.sleep(sleep_time)

def runFilling(self):
    print("runFilling")
    fillingRunTime = .5
    cutTime = .2
    #sleep_time = STAGE_TIME - fillingRunTime - cutTime * 2
    #gpio.output(FILLIG_EXT, #gpio.LOW)
    #self.extendExtruder_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(fillingRunTime) # Number of seconds that the pi will sleep
    #gpio.output(FILLIG_EXT, #gpio.HIGH)
    #self.extendExtruder_button.SetBackgroundColour(INACTIVE_COLOR)
    #gpio.ouptut(CUT_EXT, #gpio.LOW)
    #self.extendWorm_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(cutTime)
    #gpio.ouptut(CUT_EXT, #gpio.HIGH)
    #self.extendWorm_button.SetBackgroundColour(INACTIVE_COLOR)
    #gpio.ouptut(CUT_RET, #gpio.LOW)
    #self.retractWorm_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(cutTime)
    #gpio.ouptut(CUT_RET, #gpio.HIGH)
    #self.retractWorm_button.SetBackgroundColour(INACTIVE_COLOR)
    #time.sleep(sleep_time)

def runChocPump2(self):
    print("runChocPump2")
    runTime = .5
    #sleep_time = STAGE_TIME - runTime
    #gpio.output(CHOC_PUMP_2, #gpio.LOW)
    #self.runChocPump2_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(runTime) # Number of seconds that the pi will sleep
    #gpio.output(CHOC_PUMP_2, #gpio.HIGH)
    #self.runChocPump2_button.SetBackgroundColour(INACTIVE_COLOR)
    #time.sleep(sleep_time)

#################################################################
# Functions to control individual components
#################################################################
def extendActuator(arg):
    print("extendActuator")
    #gpio.output(ACTUATOR_EXT, #gpio.LOW)
    arg.extendActuator_button.SetBackgroundColour(ACTIVE_COLOR)
    time.sleep(5)
    #gpio.output(ACTUATOR_RET, #gpio.HIGH)
    arg.extendActuator_button.SetBackgroundColour(INACTIVE_COLOR)
    time.sleep(.3)
    
def retractActuator(self):
    print("retractActuator")
    #gpio.output(ACTUATOR_RET, #gpio.LOW)
    self.retractActuator_button.SetBackgroundColour(ACTIVE_COLOR)
    #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
    self.retractActuator_button.SetBackgroundColour(INACTIVE_COLOR)
    time.sleep(.3)
# End of our states.