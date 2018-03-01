#!/usr/bin/env python

import wx
import images
import time
import threading
from threading import Thread
import RPi.GPIO as GPIO

# Set numbering mode for the program
GPIO.setmode(GPIO.BOARD)

# The following variabes should be considered costants
ACTUATOR_EXT = 40
ACTUATOR_RET = 38
CHOC_PUMP_BOT = 36
FILLIG_EXT = 32
FILLING_RET = 26
CHOC_PUMP_TOP = 24
#26, 24, 22

# Setup the GPIO pins
GPIO.setup(ACTUATOR_RET, GPIO.OUT)
GPIO.setup(ACTUATOR_EXT, GPIO.OUT)
GPIO.output(ACTUATOR_EXT, GPIO.HIGH)
GPIO.output(ACTUATOR_RET, GPIO.HIGH)

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

        b = wx.Button(self, 10, "Extend Actuator", (20, 80))
        self.Bind(wx.EVT_BUTTON, self.ExtendAcutator, b)
        #b.SetDefault()
        #b.SetSize(b.GetBestSize())

        b = wx.Button(self, 20, "Reset Actuator", (20, 140))
        self.Bind(wx.EVT_BUTTON, self.RetractActuator, b)
        #b.SetToolTip("This is a Hello button...")
        
        b = wx.Button(self, 25, "EMERGENCY STOP", (20, 200))
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
        
    def Start_event(self, event):
        print ("Hello, Python!")
        #thread = Thread(target = threaded_function, args = (10,))
        #thread.start()
        #thread.join()
        #print ("thread finished...exiting")
        try:
            while(onoff): #fix this True value to do something that can thread, etc.
                GPIO.output(ACTUATOR_RET, GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                GPIO.output(ACTUATOR_RET, GPIO.LOW)
                GPIO.output(40, GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                GPIO.output(40, GPIO.LOW)
        except KeyboardInterrupt:
            GPIO.cleanup()
        
    def ExtendAcutator(self, event):
        GPIO.output(40, GPIO.LOW)
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        
    def RetractActuator(self, event):
        GPIO.output(ACTUATOR_RET, GPIO.LOW)
        GPIO.output(40, GPIO.HIGH)
    
    def EmergencyStop(self, event):
        GPIO.output(ACTUATOR_RET, GPIO.HIGH)
        GPIO.output(40, GPIO.HIGH)
        onoff = False
        
    def TestButton(self, event):      

        t = myThread()
        t.start()
        

        
class myThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
                 
                 
    def run(self):
        print ("Inside my thread!")
        #logging.dubug('Current GPIO pin %s')
        try:
            while(onoff): #fix this True value to do something that can thread, etc.
                GPIO.output(ACTUATOR_RET, GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                GPIO.output(ACTUATOR_RET, GPIO.LOW)
                GPIO.output(40, GPIO.HIGH)
                time.sleep(3) # Number of seconds that the pi will sleep
                GPIO.output(40, GPIO.LOW)
                #if (EmergencyStop()) False
        except KeyboardInterrupt:
                GPIO.cleanup()
                      
        #logging.debug('ending')
        
#----------------------------------------------------------------------

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

#----------------------------------------------------------------------


overview = """<html><body>
<h2>Button</h2>

A button is a control that contains a text string or a bitmap and can be
placed on nearly any kind of window.

</body></html>
"""



if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
