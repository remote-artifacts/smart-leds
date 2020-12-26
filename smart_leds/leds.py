from machine import Pin, PWM
import time
import uasyncio as asyncio

class Leds:
    def __init__(self, pin_mapping=None):
        if pin_mapping is None:
            pin_mapping = {
                "red": 23,
                "green": 19,
                "blue": 18,
                "white": 4
            }

        leds = {}
        for name, pin in pin_mapping.items():
            leds[name] = PWM(Pin(pin), freq=1000, duty=0)

        self.pin_mapping = pin_mapping
        self.leds = leds

    def flash(self, duration=0.1, **colors):
        if len(colors) == 0:
            colors = {color: 500 for color in self.leds}

        self.set(**colors)
        time.sleep(duration)
        self.off_all()

    def off(self, color):
        self.leds[color].duty(0)

    def off_all(self):
        for color in self.leds:
            self.leds[color].duty(0)

    def set(self, **colors):
        for color, value in colors.items():
            self.leds[color].duty(value)

    def get(self, color):
        return self.leds[color].duty()

    def fade(self, color, start=0, end=1000, duration=1000):

        if start > end:
            step_duration = duration / (start - end)
            values = reversed(range(end, start + 1))
        else:
            step_duration = duration / (end - start)
            values = range(start, end + 1)

        for step in values:
            self.set(**{color: step})
            time.sleep(step_duration/1000)

    async def afade(self, color, start=0, end=1000, duration=1000):
        if start > end:
            step_duration = duration / (start - end) * 10
            values = reversed(range(end, start + 1, 10))
        else:
            step_duration = duration / (end - start) * 10
            values = range(start, end + 1, 10)

        for step in values:
            #print(step)
            self.set(**{color: step})
            await asyncio.sleep(step_duration/1000)
