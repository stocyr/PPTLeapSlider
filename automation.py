# -*- coding: iso-8859-1 -*-

import ctypes
import time
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture, Vector

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKey(hexKeyCode): # http://msdn.microsoft.com/en-us/library/ms927178.aspx

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))



class SampleListener(Leap.Listener):
    timestamp = 0
    
    def on_init(self, controller):
        print "Leap API connection established"

    def on_connect(self, controller):
        print "Device connected"
        print
        # enable swipe gesture and configure it
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        configur = controller.config
        configur.set("Gesture.Swipe.MinLength",50.0)
        configur.set("Gesture.Swipe.MinVelocity",200.0)
        if(configur.set("Gesture.Swipe.MinLength",50.0) and configur.set("Gesture.Swipe.MinVelocity",200.0)):
            configur.save()
        
        # enable background frame reception
        controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES);

    def on_disconnect(self, controller):
        print "Device disconnected"

    def on_exit(self, controller):
        print "Leap App exited"

    def on_frame(self, controller):
        # Get the most recent frame
        frame = controller.frame()

        if not frame.hands.empty:
            # Handle gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    #print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                    #        gesture.id, self.state_string(gesture.state),
                    #        swipe.position, swipe.direction, swipe.speed)
                    
                    #print "%s  - state: %d" % (swipe.direction, swipe.state)
                    
                    #if swipe.direction.angle_to(Vector(-1, 0, 0))*180.0/3.14159265 < 90 and swipe.state == 1:
                    if swipe.direction.x < 0 and swipe.state == 1 and (frame.timestamp - self.timestamp) > 150000:
                        # if the swipe was directed to the left: generate slide swipe key
                        self.timestamp = frame.timestamp
                        print
                        print 'Swipe (ID %d) position: %s speed: %.1f mm/s' % (gesture.id, swipe.position, swipe.speed)
                        PressKey(13)
                        ReleaseKey(13)
                            
def main():
    # Create a listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "(Press Enter to quit)"
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
