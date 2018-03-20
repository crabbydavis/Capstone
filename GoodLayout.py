#!/usr/bin/python
# -*- coding: utf-8 -*
# choclateFactory.py

import wx
import time
from threading import Thread
import RPi.GPIO as GPIO
from enum import Enum

# The following variabes should be considered costants

MAX_STEPS_EXTRUDER = 1000
MAX_MOLDS = 6

#GPIO pins
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
FILLIG_EXT = 32
FILLING_RET = 26
CHOC_PUMP_2 = 24
CUT_EXT = 22
CUT_RET = 18
#16 12 ARE STILL AVAILABLE ON THE ONE SIDE

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
GPIO.setmode(GPIO.BOARD)

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
        
    #start_button = wx.Button(self, label="START")
    
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
        start_button = wx.Button(self, label="START")
        start_button.SetBackgroundColour('#42f465')
        self.Bind(wx.EVT_BUTTON, Start_event, start_button)
        emergencyStop_button = wx.Button(self, label="EMERGENCY STOP")
        emergencyStop_button.SetBackgroundColour('#f44242')
        self.Bind(wx.EVT_BUTTON, self.Start_event, emergencyStop_button)

        # Actuator
        extendActuator_button = wx.Button(self, label="Extend Actuator")
        self.Bind(wx.EVT_BUTTON, self.extendActuator, extendActuator_button)
        retractActuator_button = wx.Button(self, label="Retract Actuator")
        self.Bind(wx.EVT_BUTTON, self.Start_event, retractActuator_button)
        stopActuator_button = wx.Button(self, label="Stop Actuator")
        self.Bind(wx.EVT_BUTTON, self.Start_event, stopActuator_button)
        
        # Chocolate Pump 1
        runChocPump1_button = wx.Button(self, label="Run Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.Start_event, runChocPump1_button)
        stopChocPump1_button = wx.Button(self, label="Stop Choc. Pump 1")
        self.Bind(wx.EVT_BUTTON, self.Start_event, stopChocPump1_button)

        # Filling Extruder
        extendExtruder_button = wx.Button(self, label="Extend Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, extendExtruder_button)
        retractExtruder_button = wx.Button(self, label="Retract Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, retractExtruder_button)
        stopExtruder_button = wx.Button(self, label="Stop Extruder")
        self.Bind(wx.EVT_BUTTON, self.Start_event, stopExtruder_button)

        # Worm Gear
        extendWorm_button = wx.Button(self, label="Extend Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, extendWorm_button)
        retractWorm_button = wx.Button(self, label="Retract Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, retractWorm_button)
        stopWorm_button = wx.Button(self, label="Stop Piano Wire")
        self.Bind(wx.EVT_BUTTON, self.Start_event, stopWorm_button)

        # Chocolate Pump 2
        runChocPump2_button = wx.Button(self, label="Run Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.Start_event, runChocPump2_button)
        stopChocPump2_button = wx.Button(self, label="Stop Choc. Pump 2")
        self.Bind(wx.EVT_BUTTON, self.Start_event, stopChocPump2_button)

        # Setup the display to be a grid of all of the buttons
        vbox = wx.BoxSizer(wx.VERTICAL)
        #self.display = wx.TextCtrl(self, style=wx.TE_RIGHT)
        #vbox.Add(self.display, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        gs = wx.GridSizer(4, 5, 5, 5)

        gs.AddMany( [(wx.StaticText(self), wx.EXPAND),
            (start_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (emergencyStop_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            # Second Row
            (extendActuator_button, 0, wx.EXPAND),
            (runChocPump1_button, 0, wx.EXPAND),
            (extendExtruder_button, 0, wx.EXPAND),
            (extendWorm_button, 0, wx.EXPAND),
            (runChocPump2_button, 0, wx.EXPAND),
            # Third Row
            (retractActuator_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (retractExtruder_button, 0, wx.EXPAND),
            (retractWorm_button, 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            # Fourth Row
            (stopActuator_button, 0, wx.EXPAND),
            (stopChocPump1_button, 0, wx.EXPAND),
            (stopExtruder_button, 0, wx.EXPAND),
            (stopWorm_button, 0, wx.EXPAND),
            (stopChocPump2_button, 0, wx.EXPAND) ])

        vbox.Add(gs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)

        def Start_event(self, event):
            win = Popup(self.GetTopLevelParent(), wx.SIMPLE_BORDER)

            btn = event.GetEventObject()
            pos = btn.ClientToScreen( (0,0) )
            sz =  btn.GetSize()
            win.Position(pos, (0, sz[1]))
            time.sleep(.1) # Have a slight delay before the popup shows
            win.Show(True)
            thread = Thread(target = threaded_function, args = (win,))
            thread.start()
            extendActuator_button.SetBackgroundColour('#42f465')
            thread.join()
	    while True:	current_st	
		
	
    # The following are the vairous states that the factory can be in
    #################################################################
    def init_st():
        runTime = 5
        sleep_time = STAGE_TIME - runTime
        current_st = State.START1

    def start1_st():
        runChocPump1
        current_st = State.START2
    
    def start2_st():
        runChocPump1
        runFilling
        current_st = State.RUN

    def run_st():
        runChocPump1
        runFilling
        runChocPump2
        current_st = State.END2

    def end2_st():
        runFilling
        runChocPump2
        current_st = State.END1

    def end1_st():
        runChocPump2
        current_st = State.FINISH

    def finish_st():
        current_st = State.FINISH

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
    def runChocPump1():
        runTime = 5
        sleep_time = STAGE_TIME - runTime
        GPIO.output(CHOC_PUMP_1, GPIO.LOW)
        time.sleep(run_time) # Number of seconds that the pi will sleep
        GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
        time.sleep(sleep_time)

    def runFilling():
        fillingRunTime = 5
        cutTime = 2
        sleep_time = STAGE_TIME - fillingRunTime - cutTime * 2
        GPIO.output(FILLIG_EXT, GPIO.LOW)
        time.sleep(fillingRunTime) # Number of seconds that the pi will sleep
        GPIO.output(FILLIG_EXT, GPIO.HIGH)
        GPIO.ouptut(CUT_EXT, GPIO.LOW)
        time.sleep(cutTime)
        GPIO.ouptut(CUT_EXT, GPIO.HIGH)
        GPIO.ouptut(CUT_RET, GPIO.LOW)
        time.sleep(cutTime)
        GPIO.ouptut(CUT_RET, GPIO.HIGH)
        time.sleep(sleep_time)

    def runChocPump2():
        runTime = 5
        sleep_time = STAGE_TIME - runTime
        GPIO.output(CHOC_PUMP_2, GPIO.LOW)
        time.sleep(run_time) # Number of seconds that the pi will sleep
        GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
        time.sleep(sleep_time)
    #################################################################

    # Functions to control individual components
    #################################################################
    def extendActuator(self, event):
        GPIO.output(ACTUATOR_EXT, GPIO.LOW)
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        time.sleep(3)
        
    def retractActuator(self, event):
        GPIO.output(ACTUATOR_RET, GPIO.LOW)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
        time.sleep(3)

    def stopActuator(self, event):
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
    
    def runChocPump1():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def stopChocPump1():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def extendExtruder():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
   
    def retractExtruder():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def stopExtruder():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def extendWorm():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def retractWorm():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def stopWorm():
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)

    def emergencyStop(self, event):
        GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(CHOC_PUMP_1, GPIO.HIGH)
        GPIO.output(FILLIG_EXT, GPIO.HIGH)
        GPIO.output(FILLING_RET, GPIO.HIGH)
        GPIO.output(CHOC_PUMP_2, GPIO.HIGH)
        GPIO.output(CUT_EXT, GPIO.HIGH)
        GPIO.output(CUT_RET, GPIO.HIGH)

        # Make sure all molds with chocolate in them get pushed out
        for i in range(0, MAX_MOLDS):
            self.extendActuator
            self.retractActuator

        onoff = False
    #################################################################

def threaded_function(arg):
    time.sleep(3)
    arg.Show(False)
    #for i in range(arg):
        #print("running")
        #time.sleep(1)

if __name__ == '__main__':
  
    app = wx.App()
    Main(None, title='Bouchard Chocolate Factory')
    app.MainLoop()
