# coding: utf-8
import os
import sys
from time import sleep
from threading import Timer, Thread
from Queue import Queue

import pygame
from evdev import InputDevice, categorize, ecodes

events_mm = Queue()

if os.path.islink('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-event-kbd'):
    dev = InputDevice('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-event-kbd')
elif os.path.islink('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-if01-event-mouse'):
    dev = InputDevice('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-if01-event-mouse')
else:
    print "No MakeyMakey/Arduino Leonardo found:-("
    sys.exit(1)

def worker():
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            events_mm.put(event)

t1 = Thread(target=worker)
t1.start()



# def Sound(object):

def go():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("/home/tyrus/MuseoMixESt/projet/music.mp3")
        pygame.mixer.music.play()



pygame.mixer.init()


gaming = True
while gaming:
    try:
        if not events_mm.empty():
            event = events_mm.get_nowait()
            code = event.code
            print code
            if code == ecodes.KEY_SPACE:
                print "Début du jeu"
                go()
        sleep(0.1)
    except Exception,e:
        # t1.terminate()
        # t2.terminate()
        print "BUG"
        print e
        sys.exit(0)

pygame.quit()
