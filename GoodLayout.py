#!/usr/bin/python
# -*- coding: utf-8 -*
# choclateFactory.py

import wx
import time
from threading import Thread
#import RPi.#gpio as #gpio
from enum import Enum

# The following variabes should be considered costants

MAX_STEPS_EXTRUDER = 1000
MAX_MOLDS = 6

##gpio pins
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
FILLIG_EXT = 32
FILLING_RET = 26
CHOC_PUMP_2 = 24
CUT_EXT = 22
CUT_RET = 18
#16 12 ARE STILL AVAILABLE ON THE ONE SIDE

STAGE_TIME = 90
ACTIVE_COLOR = '#42f48c'
INACTIVE_COLOR = '#f7f7f7'

class State(Enum):
    INIT = 1 
    START1 = 2
    START2 = 3
    RUN = 4
    END2 = 5
    END1 = 6
    FINISH = 7 

current_st = State.INIT

onoff = True

# Set numbering mode for the program
#gpio.setmode(#gpio.BOARD)

# Setup the #gpio pins
#gpio.setup(ACTUATOR_RET, #gpio.OUT)
#gpio.setup(ACTUATOR_EXT, #gpio.OUT)
#gpio.setup(CHOC_PUMP_1, #gpio.OUT)
#gpio.setup(FILLIG_EXT, #gpio.OUT)
#gpio.setup(FILLING_RET, #gpio.OUT)
#gpio.setup(CHOC_PUMP_2, #gpio.OUT)

#gpio.output(ACTUATOR_RET, #gpio.HIGH)
#gpio.output(ACTUATOR_EXT, #gpio.HIGH)
#gpio.output(CHOC_PUMP_1, #gpio.HIGH)
#gpio.output(FILLIG_EXT, #gpio.HIGH)
#gpio.output(FILLING_RET, #gpio.HIGH)
#gpio.output(CHOC_PUMP_2, #gpio.HIGH)

class Popup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)

        panel = wx.Panel(self)
        self.panel = panel
        panel.SetBackgroundColour("CADET BLUE")

        st = wx.StaticText(panel, -1, "Factory Started!", pos=(-1,-1))
        self.SetSize(200,50)
        #self.CenterOnParent()
        panel.SetSize(200,50)
        wx.CallAfter(self.Refresh)

class Main(wx.Frame):
    def __init__(self, parent, title):
        super(Main, self).__init__(parent, title=title, 
            size=(300, 250))
            
        self.InitUI()
        self.Move((0, 0))
        self.Maximize()
        self.Show()     
            
    def InitUI(self):
       # The following is the code for a menu bar
        #menubar = wx.MenuBar()
        #fileMenu = wx.Menu()
        #menubar.Append(fileMenu, '&File')
        #self.SetMenuBar(menubar)

        #def Start_event(self, event):
            #win = Popup(self.GetTopLevelParent(), wx.SIMPLE_BORDER)

            #btn = event.GetEventObject()
            #pos = btn.ClientToScreen( (0,0) )
            #sz =  btn.GetSize()
            #win.Position(pos, (0, sz[1]))
            #time.sleep(.1) # Have a slight delay before the popup shows
            #win.Show(True)
            #thread = Thread(target = threaded_function, args = (win,))
            #thread.start()
            #extendActuator_button.SetBackgroundColour('#42f465')
            #thread.join()

        # Define All of the Buttons that need to be added
        self.start_button = wx.Button(self, label="START")
        self.start_button.SetBackgroundColour('#42f465')
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.start_button)
        emergencyStop_button = wx.Button(self, label="EMERGENCY STOP")
        emergencyStop_button.SetBackgroundColour('#f44242')
        self.Bind(wx.EVT_BUTTON, self.Start_event, emergencyStop_button)

        # Actuator
        self.extendActuator_button = wx.Button(self, label="Extend Actuator")
        self.Bind(wx.EVT_BUTTON, self.extendActuator, self.extendActuator_button)
        self.retractActuator_button = wx.Button(self, label="Retract Actuator")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.retractActuator_button)
        self.stopActuator_button = wx.Button(self, label="Stop Actuator")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.stopActuator_button)
        
        # Chocolate Pump 1
        self.runChocPump1_button = wx.Button(self, label="Run Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.runChocPump1_button)
        self.stopChocPump1_button = wx.Button(self, label="Stop Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.stopChocPump1_button)

        # Filling Extruder
        self.extendExtruder_button = wx.Button(self, label="Extend Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.extendExtruder_button)
        self.retractExtruder_button = wx.Button(self, label="Retract Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.retractExtruder_button)
        self.stopExtruder_button = wx.Button(self, label="Stop Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.stopExtruder_button)

        # Worm Gear
        self.extendWorm_button = wx.Button(self, label="Extend Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.extendWorm_button)
        self.retractWorm_button = wx.Button(self, label="Retract Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.retractWorm_button)
        self.stopWorm_button = wx.Button(self, label="Stop Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.stopWorm_button)

        # Chocolate Pump 2
        self.runChocPump2_button = wx.Button(self, label="Run Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.runChocPump2_button)
        self.stopChocPump2_button = wx.Button(self, label="Stop Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.Start_event, self.stopChocPump2_button)

        # Setup the display to be a grid of all of the buttons
        vbox = wx.BoxSizer(wx.VERTICAL)
        #self.display = wx.TextCtrl(self, style=wx.TE_RIGHT)
        #vbox.Add(self.display, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        gs = wx.GridSizer(4, 5, 5, 5)

        gs.AddMany( [(wx.StaticText(self), wx.EXPAND),
            (self.start_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (emergencyStop_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            # Second Row
            (self.extendActuator_button, 0, wx.EXPAND),
            (self.runChocPump1_button, 0, wx.EXPAND),
            (self.extendExtruder_button, 0, wx.EXPAND),
            (self.extendWorm_button, 0, wx.EXPAND),
            (self.runChocPump2_button, 0, wx.EXPAND),
            # Third Row
            (self.retractActuator_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (self.retractExtruder_button, 0, wx.EXPAND),
            (self.retractWorm_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            # Fourth Row
            (self.stopActuator_button, 0, wx.EXPAND),
            (self.stopChocPump1_button, 0, wx.EXPAND),
            (self.stopExtruder_button, 0, wx.EXPAND),
            (self.stopWorm_button, 0, wx.EXPAND),
            (self.stopChocPump2_button, 0, wx.EXPAND) ])

        vbox.Add(gs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)

    def Start_event(self, event):
        #win = Popup(self.GetTopLevelParent(), wx.SIMPLE_BORDER)
        #btn = event.GetEventObject()
        #pos = btn.ClientToScreen( (0,0) )
        #sz =  btn.GetSize()
        #win.Position(pos, (0, sz[1]))
        #time.sleep(.1) # Have a slight delay before the popup shows
        #win.Show(True)
        self.start_button.SetBackgroundColour(ACTIVE_COLOR)
        thread = Thread(target = threaded_function, args = ([current_st,self],))
        thread.start()
        #thread.join()
	    #while True:	current_st	
		
	#################################################################
    # The following are the vairous states that the factory can be in
    #################################################################
    def init_st(arg=None):
        runTime = 5
        print("In the init_st")
        #sleep_time = STAGE_TIME - runTime
        current_st = State.START1
        return current_st

    def start1_st(arg=None):
        print("In the start1_st")
        arg.extendActuator()
        arg.runChocPump1()
        arg.retractActuator()
        current_st = State.START2
        return current_st
    
    def start2_st(arg=None):
        print("In the start2_st")
        arg.extendActuator()
        arg.runChocPump1()
        arg.runFilling()
        arg.retractActuator()
        current_st = State.RUN
        return current_st

    def run_st(arg=None):
        print("In the run_st")
        arg.extendActuator()
        arg.runChocPump1()
        arg.runFilling()
        arg.runChocPump2()
        arg.retractActuator()
        current_st = State.END2
        return current_st

    def end2_st(arg=None):
        arg.extendActuator()
        arg.runFilling()
        arg.runChocPump2()
        arg.retractActuator()
        current_st = State.END1
        return current_st

    def end1_st(arg=None):
        arg.extendActuator()
        arg.runChocPump2()
        arg.retractActuator()
        current_st = State.FINISH
        return current_st

    def finish_st(arg=None):
        current_st = State.FINISH
        return current_st

    options = {
        State.INIT : init_st,
        State.START1 : start1_st,
        State.START2 : start2_st,
        State.RUN : run_st,
        State.END2 : end2_st,
        State.END1 : end1_st,
        State.FINISH : finish_st
    }

    #################################################################
    # Functions for running the chocolate processes of the machine
    #################################################################
    def runChocPump1(self):
        print("runChocPump1")
        runTime = 5
        #sleep_time = STAGE_TIME - runTime
        #gpio.output(CHOC_PUMP_1, #gpio.LOW)
        self.runChocPump1_button.SetBackgroundColour(ACTIVE_COLOR)
        time.sleep(runTime) # Number of seconds that the pi will sleep
        #gpio.output(CHOC_PUMP_1, #gpio.HIGH)
        self.runChocPump1_button.SetBackgroundColour(INACTIVE_COLOR)
        #time.sleep(sleep_time)

    def runFilling(self):
        fillingRunTime = 5
        cutTime = 2
        #sleep_time = STAGE_TIME - fillingRunTime - cutTime * 2
        #gpio.output(FILLIG_EXT, #gpio.LOW)
        self.extendExtruder_button.SetBackgroundColour(ACTIVE_COLOR)
        time.sleep(fillingRunTime) # Number of seconds that the pi will sleep
        #gpio.output(FILLIG_EXT, #gpio.HIGH)
        self.extendExtruder_button.SetBackgroundColour(INACTIVE_COLOR)
        #gpio.ouptut(CUT_EXT, #gpio.LOW)
        self.extendWorm_button.SetBackgroundColour(ACTIVE_COLOR)
        time.sleep(cutTime)
        #gpio.ouptut(CUT_EXT, #gpio.HIGH)
        self.extendWorm_button.SetBackgroundColour(INACTIVE_COLOR)
        #gpio.ouptut(CUT_RET, #gpio.LOW)
        self.retractWorm_button.SetBackgroundColour(ACTIVE_COLOR)
        time.sleep(cutTime)
        #gpio.ouptut(CUT_RET, #gpio.HIGH)
        self.retractWorm_button.SetBackgroundColour(INACTIVE_COLOR)
        #time.sleep(sleep_time)

    def runChocPump2(self):
        runTime = 5
        #sleep_time = STAGE_TIME - runTime
        #gpio.output(CHOC_PUMP_2, #gpio.LOW)
        self.runChocPump2_button.SetBackgroundColour(ACTIVE_COLOR)
        time.sleep(run_time) # Number of seconds that the pi will sleep
        #gpio.output(CHOC_PUMP_2, #gpio.HIGH)
        self.runChocPump2_button.SetBackgroundColour(INACTIVE_COLOR)
        #time.sleep(sleep_time)

    #################################################################
    # Functions to control individual components
    #################################################################
    def extendActuator(self):
        print("extendActuator")
        #gpio.output(ACTUATOR_EXT, #gpio.LOW)
        self.extendActuator_button.SetBackgroundColour(ACTIVE_COLOR)
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        self.retractActuator_button.SetBackgroundColour(INACTIVE_COLOR)
        time.sleep(3)
        
    def retractActuator(self):
        print("retractActuator")
        #gpio.output(ACTUATOR_RET, #gpio.LOW)
        self.retractActuator_button.SetBackgroundColour(ACTIVE_COLOR)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        self.extendActuator_button.SetBackgroundColour(INACTIVE_COLOR)
        time.sleep(3)

    def stopActuator():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    
    #def runChocPump1():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        #time.sleep(3)
    def stopChocPump1():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def extendExtruder():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def retractExtruder():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def stopExtruder():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def extendWorm():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def retractWorm():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def stopWorm():
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        time.sleep(3)
    def emergencyStop(self, event):
        #gpio.output(ACTUATOR_EXT, #gpio.HIGH)
        #gpio.output(ACTUATOR_RET, #gpio.HIGH)
        #gpio.output(CHOC_PUMP_1, #gpio.HIGH)
        #gpio.output(FILLIG_EXT, #gpio.HIGH)
        #gpio.output(FILLING_RET, #gpio.HIGH)
        #gpio.output(CHOC_PUMP_2, #gpio.HIGH)
        #gpio.output(CUT_EXT, #gpio.HIGH)
        #gpio.output(CUT_RET, #gpio.HIGH)

        # Make sure all molds with chocolate in them get pushed out
        for i in range(0, MAX_MOLDS):
            self.extendActuator
            self.retractActuator

        onoff = False
    #################################################################

def threaded_function(arg):
    time.sleep(3)
    #arg.Show(False)
    current_st = arg[0]
    while True:
        current_st = arg[1].options[current_st](arg[1])


if __name__ == '__main__':
  
    app = wx.App()
    Main(None, title='Bouchard Chocolate Factory')
    app.MainLoop()
