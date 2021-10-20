# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from threading import Thread
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


class ProjectNameGUI(App):
    pass
# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1,.1, 1) # (WHITE)

cyprus.open_spi()
cyprus.initialize()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()
arm = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=1)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    armPosition = 0
    lastClick = time.clock()
    OnOff2 = True
    OnOff = True
    magText = ""
    armText = ""

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        if self.OnOff2 == True:
            self.armText = "Raise Arm"
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            self.armControl.text = self.armText
            self.OnOff2 = False
            return
        else:
            self.armText = "Lower Arm"
            self.armControl.text = self.armText
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            self.OnOff2 = True

    def toggleMagnet(self):
        if self.OnOff == True:
            self.magText = "Drop Ball"
            cyprus.set_servo_position(2, 1)
            self.magnetControl.text = self.magText
            self.OnOff = False
            return
        else:
            self.magText = "Hold Ball"
            self.magnetControl.text = self.magText
            cyprus.set_servo_position(2, .5)
            self.OnOff = True
        
    def auto(self):
        if cyprus.read_gpio() & 0b0001 == 0:

            arm.go_to_position(1.54)
            sleep(2.0)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.0)
            cyprus.set_servo_position(2, 1)
            sleep(1.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.5)
            arm.go_to_position(1.18)
            sleep(2.0)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.5)
            cyprus.set_servo_position(2, .5)
            sleep(1.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        else:

            arm.go_to_position(1.18)
            sleep(2.0)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.0)
            cyprus.set_servo_position(2, 1)
            sleep(1.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.5)
            arm.go_to_position(1.54)
            sleep(2.0)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1.5)
            cyprus.set_servo_position(2, .5)
            sleep(1.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)






    def setArmPosition(self, position):
        arm.go_to_position(position / 40)

    def homeArm(self):
        arm.home(self.homeDirection)
        
    def isBallOnTallTower(self):

        while True:

            if cyprus.read_gpio() & 0b0001 == 0:
                    print("detected on big tower")
                    sleep(1.0)
            else:
                sleep(1.0)

    def start_button_thread2(self):
        Thread(target=self.isBallOnTallTower).start()

    def start_button_thread(self):
        Thread(target=self.isBallOnShortTower).start()

    def isBallOnShortTower(self):
        while True:

            if cyprus.read_gpio() & 0b0010 == 0:
                print("detected on small tower")
                sleep(1.0)
            elif cyprus.read_gpio() & 0b0001 == 0:
                print("detected on big tower")
                sleep(1.0)
            else:
                sleep(1.0)
        
    def initialize(self):
        arm.go_until_press(1, 6400)
        sleep(2.0)
        arm.set_as_home()

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()
    
sm.add_widget(MainScreen(name = 'main'))


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
