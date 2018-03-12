#!/usr/bin/env python

import wx
import images
import time
import threading
from threading import Thread
from enum import Enum, auto
#import RPi.#GPIO as #GPIO

# Set numbering mode for the program
#GPIO.setmode(#GPIO.BOARD)

# The following variabes should be considered costants
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_1 = 36
FILLIG_EXT = 32
FILLING_RET = 26
CHOC_PUMP_2 = 24
CUT_EXT = 22
CUT_RET = 18
#16 12 ARE STILL AVAILABLE ON THE ONE SIDE

# Setup the #GPIO pins
#GPIO.setup(ACTUATOR_RET, #GPIO.OUT)
#GPIO.setup(ACTUATOR_EXT, #GPIO.OUT)
#GPIO.output(ACTUATOR_EXT, #GPIO.HIGH)
#GPIO.output(ACTUATOR_RET, #GPIO.HIGH)

STAGE_TIME = 90 # Each stage should take 90s
ACTUATOR_TIME = 3 # Give the actuator 3s to extend and retract

class State(Enum):
    INIT = auto()
    START1 = auto()
    START2 = auto()
    RUN = auto()
    END2 = auto()
    END1 = auto()
    FINISH = auto()

current_st = State.INIT

onoff = True

#----------------------------------------------------------------------

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent, -1,
                         style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.log = log
        
        b = wx.Button(self, 5, "START", (20, 20))
        self.Bind(wx.EVT_BUTTON, self.Start_event, b)
        #b.SetToolTip("This is a Hello button...")
        b = wx.Button(self, 25, "EMERGENCY STOP", (160, 20))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)

        # Actuator
        b = wx.Button(self, 10, "Extend Actuator", (20, 80))
        self.Bind(wx.EVT_BUTTON, self.ExtendAcutator, b, ACTUATOR_EXT)
        #b.SetDefault()
        #b.SetSize(b.GetBestSize())
        b = wx.Button(self, 20, "Retract Actuator", (20, 140))
        self.Bind(wx.EVT_BUTTON, self.RetractActuator, b)
        #b.SetToolTip("This is a Hello button...")
        b = wx.Button(self, 20, "Stop Actuator", (20, 200))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        #b.SetToolTip("This is a Hello button...")
        
        # Chocolate Pump 1
        b = wx.Button(self, 20, "Run Chocolate Pump 1", (160, 80))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        b = wx.Button(self, 20, "Stop Chocolate Pump 1", (160, 140))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)

        # Filling Extruder
        b = wx.Button(self, 20, "Extend Extruder", (300, 80))
        self.Bind(wx.EVT_BUTTON, self.RetractActuator, b)
        b = wx.Button(self, 20, "Retract Extruder", (300, 140))
        self.Bind(wx.EVT_BUTTON, self.RetractActuator, b)
        b = wx.Button(self, 20, "Stop Extruder", (300, 200))
        self.Bind(wx.EVT_BUTTON, self.RetractActuator, b)

        # Worm Gear
        b = wx.Button(self, 20, "Extend Extruder", (480, 80))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        b = wx.Button(self, 20, "Retract Extruder", (480, 140))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        b = wx.Button(self, 20, "Stop Extruder", (480, 200))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)

        # Chocolate Pump 2
        b = wx.Button(self, 20, "Run Chocolate Pump 2", (600, 80))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        b = wx.Button(self, 20, "Stop Chocolate Pump 2", (600, 140))
        self.Bind(wx.EVT_BUTTON, self.EmergencyStop, b)
        
        b = wx.Button(self, 30, "TEST BUTTON", (20, 260))
        self.Bind(wx.EVT_BUTTON, self.TestButton, b)
        

        #b = wx.Button(self, 40, "Flat Button?", (20,160), style=wx.NO_BORDER)
        #b.SetToolTip("This button has a style flag of wx.NO_BORDER.\n"
        #                  "On some platforms that will give it a flattened look.")
        #self.Bind(wx.EVT_BUTTON, self.OnClick, b)

        #b = wx.Button(self, 50, "wx.Button with icon", (20, 220))
        #b.SetToolTip("wx.Button can how have an icon on the left, right,\n"
        #                   "above or below the label.")
        #self.Bind(wx.EVT_BUTTON, self.OnClick, b)

        b.SetBitmap(images.Mondrian.Bitmap,
                    wx.LEFT    # Left is the default, the image can be on the other sides too
                    #wx.RIGHT
                    #wx.TOP
                    #wx.BOTTOM
                    )
        b.SetBitmapMargins((2,2)) # default is 4 but that seems too big to me.

        # Setting the bitmap and margins changes the best size, so
        # reset the initial size since we're not using a sizer in this
        # example which would have taken care of this for us.
        b.SetInitialSize()

        #b = wx.Button(self, 60, "Multi-line\nbutton", (20, 280))
        #b = wx.Button(self, 70, pos=(160, 280))
        #b.SetLabel("Another\nmulti-line")

    def OnClick(self, event):
        self.log.write("Click! (%d)\n" % event.GetId())
        
    #def threaded_function(arg):
    #    for i in range(arg):
    #        print ("running")
    #        sleep(1)
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

    def Start_event(self, event):
        print ("Hello, Python!")
        #thread = Thread(target = threaded_function, args = (10,))
        #thread.start()
        #thread.join()
        #print ("thread finished...exiting")
        try:
            # Move the actuator forward and back and then do actions for stages
            while(onoff): #fix this True value to do something that can thread, etc.
                #GPIO.output(ACTUATOR_EXT, GPIO.LOW)
                time.sleep(ACTUATOR_TIME) # Number of seconds that the pi will sleep
                #GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
                #GPIO.output(ACTUATOR_RET, GPIO.LOW)
                time.sleep(ACTUATOR_TIME) # Number of seconds that the pi will sleep
                #GPIO.output(ACTUATOR_RET, GPIO.HIGH)
                options[current_st]()
        except KeyboardInterrupt:
            #GPIO.cleanup()
            time.sleep(3)

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

    def ExtendAcutator(self, event, gpio):
        #GPIO.output(ACTUATOR_EXT, #GPIO.LOW)
        #GPIO.output(ACTUATOR_RET, #GPIO.HIGH)
        print(gpio)
        time.sleep(3)
        
    def RetractActuator(self, event):
        #GPIO.output(ACTUATOR_RET, #GPIO.LOW)
        #GPIO.output(ACTUATOR_EXT, #GPIO.HIGH)
        time.sleep(3)
    
    def EmergencyStop(self, event):
        #GPIO.output(ACTUATOR_EXT, #GPIO.HIGH)
        #GPIO.output(ACTUATOR_RET, #GPIO.HIGH)
        #GPIO.output(CHOC_PUMP_1, #GPIO.HIGH)
        #GPIO.output(FILLIG_EXT, #GPIO.HIGH)
        #GPIO.output(FILLING_RET, #GPIO.HIGH)
        #GPIO.output(CHOC_PUMP_2, #GPIO.HIGH)
        #GPIO.output(CUT_EXT, #GPIO.HIGH)
        #GPIO.output(CUT_RET, #GPIO.HIGH)

        onoff = False
        
    def TestButton(self, event):      

        t = myThread()
        t.start()
        

        
class myThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
                 
                 
    def run(self):
        print ("Inside my thread!")
        #logging.dubug('Current #GPIO pin %s')
        try:
            while(onoff): #fix this True value to do something that can thread, etc.
                #GPIO.output(ACTUATOR_RET, #GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                #GPIO.output(ACTUATOR_RET, #GPIO.LOW)
                #GPIO.output(40, #GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                #GPIO.output(40, #GPIO.LOW)
                #if (EmergencyStop()) False
        except KeyboardInterrupt:
            #GPIO.cleanup()
            time.sleep(3)
                      
        #logging.debug('ending')
        
#----------------------------------------------------------------------

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

#----------------------------------------------------------------------

if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
