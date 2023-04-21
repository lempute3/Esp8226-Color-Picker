from ast import While
from concurrent.futures import thread
from tkinter.tix import Tree
from neopy import NeoPy
from enum import Enum
from threading import Thread
import random
import time


class Animations(Enum):
    SPARKLING_STAR = 1,
    RUNNING_RAINBOW = 2,
    COLOR_FADE = 3

    @staticmethod
    def from_str(text):
        statuses = [animation for animation in dir(
            Animations) if not animation.startswith('_')]
        if text in statuses:
            return getattr(Animations, text)
        return None


class Client(NeoPy):
    def __init__(self, leds, brighness, ip, port):
        NeoPy.__init__(self, leds, ip, port)

        self.setBrightness(brighness)
        self._animationWorkerSatus = False

    def setColor(self, color):
        self.setAll(color)
        self.show()

    def setGradient(self, colors, points):
        pass

    def startAnimation(self, mode, delay=None):
        self._animationWorkerSatus = True
        self._animationWorker = Thread(target=lambda: self._setAnimation(mode, delay))
        self._animationWorker.daemon = True
        self._animationWorker.start()

    def stopAnimation(self):
        self._animationWorkerSatus = False

    def _setAnimation(self, mode, delay=0.04):

        # Type checking
        if mode and not isinstance(mode, Animations):
            raise TypeError(
                'animation mode must be an instance of Animations Enum')

        while self._animationWorkerSatus:
            if mode == Animations.SPARKLING_STAR:
                self.setBrightness(self.brightness)
                self.setAll((10, 10, 10))

                pixel = random.randrange(self.numPixels())
                self.set(pixel, (255, 255, 255))
                self.show()

                time.sleep(delay)
                self.set(pixel, (180, 180, 180))
                self.show()
                time.sleep(delay)

            elif mode == Animations.RUNNING_RAINBOW:
                self.setBrightness(self.brightness)
                conv = 256 / self.numPixels()
                for j in range(self.numPixels()):
                    for i in range(self.numPixels()):
                        loc = (i+j) % self.numPixels()
                        wh = self.wheel(loc * conv)
                        self.set(i, wh)
                    self.show()
                    time.sleep(delay)

            elif mode == Animations.COLOR_FADE:
                self.setBrightness(self.brightness)
                for i in range(256):
                    for j in range(self.numPixels()):
                        self.setAll(self.wheel(i))
                    self.show()
                    time.sleep(delay)