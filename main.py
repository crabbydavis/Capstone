#!/usr/bin/python
# -*- coding: utf-8 -*
# choclateFactory.py

import wx
import time
from threading import Thread
import RPi.gpio as gpio
from enum import Enum
from multiprocessing.pool import ThreadPool
from chocolate_factory import ChocolateFactory
from state import State
from wx.lib.pubsub import pub

# gpio pins
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
CHOC_PUMP_2 = 32
#FILLING_EXT = 26
#FILLING_RET = 24
#CUT_EXT = 22
#CUT_RET = 18

ACTIVE_COLOR = '#42f48c'

class State(Enum):
    INIT = 1 
    START1 = 2
    START2 = 3
    RUN = 4
    END2 = 5
    END1 = 6
    FINISH = 7 

current_st = State.INIT

runFactory = False
factoryEvent = ''

# Set numbering mode for the program
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)

# Setup the gpio pins
gpio.setup(ACTUATOR_RET, gpio.OUT)
gpio.setup(ACTUATOR_EXT, gpio.OUT)
gpio.setup(CHOC_PUMP_1, gpio.OUT)
gpio.setup(CHOC_PUMP_2, gpio.OUT)
#gpio.setup(FILLING_EXT, gpio.OUT)
#gpio.setup(FILLING_RET, gpio.OUT)

gpio.output(ACTUATOR_RET, gpio.HIGH)
gpio.output(ACTUATOR_EXT, gpio.HIGH)
gpio.output(CHOC_PUMP_1, gpio.HIGH)
gpio.output(CHOC_PUMP_2, gpio.HIGH)
#gpio.output(FILLING_EXT, gpio.HIGH)
#gpio.output(FILLING_RET, gpio.HIGH)

class Main(wx.Frame):
    #state = State()
    def __init__(self, parent, title):
        super(Main, self).__init__(parent, title=title, 
            size=(300, 250))
            
        self.InitUI()
        self.Move((0, 0))
        self.Maximize()
        self.Show()     

        # Subscribe to events for changing the color of buttons
        pub.subscribe(self.setExtendActuatorColor, "EXTEND_ACTUATOR")
        pub.subscribe(self.setRetractActuatorColor, "RETRACT_ACTUATOR")
        pub.subscribe(self.setRunChocPump1Color, "RUN_CHOC_PUMP_1")
        pub.subscribe(self.setRunChocPump2Color, "RUN_CHOC_PUMP_2")
        #pub.subscribe(self.setExtendWireColor, "EXTEND_WIRE")
        #pub.subscribe(self.setRetractWireColor, "RETRACT_WIRE")
        #pub.subscribe(self.setExtendExtruderColor, "EXTEND_EXTRUDER")
        #pub.subscribe(self.setRetractExtruderColor, "RETRACT_EXTRUDER")
            
    def InitUI(self):
        # Define All of the Buttons that need to be added
        self.start_button = wx.Button(self, label="START")
        self.start_button.SetBackgroundColour('#42f465')
        self.Bind(wx.EVT_BUTTON, self.startFactory, self.start_button)

        self.finish_button = wx.Button(self, label="FINISH")
        self.finish_button.SetBackgroundColour('#ff6d6d')
        self.Bind(wx.EVT_BUTTON, self.finish, self.finish_button)

        emergencyStop_button = wx.Button(self, label="EMERGENCY STOP")
        emergencyStop_button.SetBackgroundColour('#f44242')
        self.Bind(wx.EVT_BUTTON, self.emergencyStop, emergencyStop_button)

        self.reset_button = wx.Button(self, label="RESET")
        self.Bind(wx.EVT_BUTTON, self.reset, self.reset_button)

        # Actuator
        self.extendActuator_button = wx.Button(self, label="Extend Actuator")
        self.Bind(wx.EVT_BUTTON, self.extendActuator, self.extendActuator_button)
        self.retractActuator_button = wx.Button(self, label="Retract Actuator")
        self.Bind(wx.EVT_BUTTON, self.retractActuator, self.retractActuator_button)
        self.stopActuator_button = wx.Button(self, label="Stop Actuator")
        self.Bind(wx.EVT_BUTTON, self.stopActuator, self.stopActuator_button)
        
        # Chocolate Pump 1
        self.runChocPump1_button = wx.Button(self, label="Run Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.runChocPump1, self.runChocPump1_button)
        self.stopChocPump1_button = wx.Button(self, label="Stop Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.stopChocPump1, self.stopChocPump1_button)

        # Filling Extruder
        #self.extendExtruder_button = wx.Button(self, label="Extend Extruder")
        #self.Bind(wx.EVT_BUTTON, self.extendExtruder, self.extendExtruder_button)
        #self.retractExtruder_button = wx.Button(self, label="Retract Extruder")
        #self.Bind(wx.EVT_BUTTON, self.retractExtruder, self.retractExtruder_button)
        #self.stopExtruder_button = wx.Button(self, label="Stop Extruder")
        #self.Bind(wx.EVT_BUTTON, self.stopExtruder, self.stopExtruder_button)

        # Wire (Worm Gear)
        #self.extendWire_button = wx.Button(self, label="Extend Piano Wire")
        #self.Bind(wx.EVT_BUTTON, self.extendWire, self.extendWire_button)
        #self.retractWire_button = wx.Button(self, label="Retract Piano Wire")
        #self.Bind(wx.EVT_BUTTON, self.retractWire, self.retractWire_button)
        #self.stopWire_button = wx.Button(self, label="Stop Piano Wire")
        #self.Bind(wx.EVT_BUTTON, self.stopWire, self.stopWire_button)

        # Chocolate Pump 2
        self.runChocPump2_button = wx.Button(self, label="Run Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.runChocPump2, self.runChocPump2_button)
        self.stopChocPump2_button = wx.Button(self, label="Stop Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.stopChocPump2, self.stopChocPump2_button)

        # Setup the display to be a grid of all of the buttons
        vbox = wx.BoxSizer(wx.VERTICAL)
        gs = wx.GridSizer(4, 5, 5, 5)

        gs.AddMany( [
            (self.start_button, 0, wx.EXPAND),
            (self.finish_button, 0, wx.EXPAND),
            (self.reset_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (emergencyStop_button, 0, wx.EXPAND),
            
            # Second Row
            (self.extendActuator_button, 0, wx.EXPAND),
            (self.runChocPump1_button, 0, wx.EXPAND),
            (self.runChocPump2_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            #(self.extendExtruder_button, 0, wx.EXPAND),
            #(self.extendWire_button, 0, wx.EXPAND),
            
            # Third Row
            (self.retractActuator_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            #(self.retractExtruder_button, 0, wx.EXPAND),
            #(self.retractWire_button, 0, wx.EXPAND),
            
            # Fourth Row
            (self.stopActuator_button, 0, wx.EXPAND),
            (self.stopChocPump1_button, 0, wx.EXPAND),
            (self.stopChocPump2_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND)
            #(self.stopExtruder_button, 0, wx.EXPAND),
            #(self.stopWire_button, 0, wx.EXPAND),
            ])

        vbox.Add(gs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)

    def startFactory(self, event):
        #self.start_button.SetBackgroundColour(ACTIVE_COLOR)
        self.extendActuator_button.SetBackgroundColour(ACTIVE_COLOR)
        thread = Thread(target = runChocolateFactory, args = (self,))
        thread.start()
	
	#################################################################
    # The following are the functions for changing the button colors
    #################################################################
    def setExtendActuatorColor(self, color):
        self.extendActuator_button.SetBackgroundColour(color)

    def setRetractActuatorColor(self, color):
        self.retractActuator_button.SetBackgroundColour(color)

    def setRunChocPump1Color(self, color):
        self.runChocPump1_button.SetBackgroundColour(color)

    def setRunChocPump2Color(self, color):
        self.runChocPump2_button.SetBackgroundColour(color)
        
    #def setExtendExtruderColor(self, color):
        #self.extendExtruder_button.SetBackgroundColour(color)
    #def setRetractExtruderColor(self, color):
        #self.retractExtruder_button.SetBackgroundColour(color)
    #def setExtendWireColor(self, color):
        #self.extendWire_button.SetBackgroundColour(color)
    #def setRetractWireColor(self, color):
        #self.retractWire_button.SetBackgroundColour(color)

    #################################################################
    # Functions to control individual components
    #################################################################
    def extendActuator(self, event):
        pass
        gpio.output(ACTUATOR_RET, gpio.HIGH)
        gpio.output(ACTUATOR_EXT, gpio.LOW) 

    def retractActuator(self, event):
        pass
        gpio.output(ACTUATOR_EXT, gpio.HIGH)
        gpio.output(ACTUATOR_RET, gpio.LOW)

    def stopActuator(self, event):
        pass
        gpio.output(ACTUATOR_RET, gpio.HIGH)
        gpio.output(ACTUATOR_EXT, gpio.HIGH)

    def runChocPump1(self, event):
        pass
        gpio.output(CHOC_PUMP_1, gpio.LOW)

    def stopChocPump1(self, event):
        pass
        gpio.output(CHOC_PUMP_1, gpio.HIGH)

    def runChocPump2(self, event):
        pass
        gpio.output(CHOC_PUMP_2, gpio.LOW)

    def stopChocPump2(self, event):
        pass
        gpio.output(CHOC_PUMP_2, gpio.HIGH)

    #def extendExtruder(self, event):        
    #def retractExtruder(self, event):
    #def stopExtruder(self, event):
    #def extendWire(self, event):
        #gpio.output(WIRE_RET, gpio.HIGH)
        #gpio.output(WIRE_EXT, gpio.LOW)
    #def retractWire(self, event):
        #gpio.output(WIRE_EXT, gpio.HIGH)
        #gpio.output(WIRE_RET, gpio.LOW)
    #def stopWire(self, event):
        #gpio.output(WIRE_EXT, gpio.HIGH)
        #gpio.output(WIRE_RET, gpio.HIGH)

    def finish(self, event):
        global factoryEvent
        runFactory = False
        factoryEvent = 'finish'

    # Do something here with killing the thread
    def emergencyStop(self, event):
        global factoryEvent
        gpio.output(ACTUATOR_EXT, gpio.HIGH)
        gpio.output(ACTUATOR_RET, gpio.HIGH)
        gpio.output(CHOC_PUMP_1, gpio.HIGH)
        gpio.output(CHOC_PUMP_2, gpio.HIGH)
        factoryEvent = "emergencyStop"
        wx.CallAfter(pub.sendMessage, "EMERGENCY_STOP")
        #gpio.output(FILLING_EXT, gpio.HIGH)
        #gpio.output(FILLING_RET, gpio.HIGH)
        #gpio.output(WIRE_EXT, gpio.HIGH)
        #gpio.output(WIRE_RET, gpio.HIGH)

    def reset(self, event):
        pass
        # Make sure all molds with chocolate in them get pushed out
        #for i in range(0, MAX_MOLDS):
         #   self.extendActuator
          #  self.retractActuator
    #################################################################

def runChocolateFactory(arg):
    print('runChocolateFactory')
    global factoryEvent
    factory = ChocolateFactory()
    runFactory = True
    factoryEvent = 'start'
    while runFactory:
        factory.on_event(factoryEvent)
        if factoryEvent == 'start':
            factoryEvent = 'run'

if __name__ == '__main__':
  
    app = wx.App()
    Main(None, title='Bouchard Chocolate Factory')
    app.MainLoop()
