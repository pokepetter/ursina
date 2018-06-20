import sys
from ursina import *

class ExitButton():

    def on_click(self):
        os._exit(0)


    def input(self, key):
        if held_keys['shift'] and key == 'q':
            self.on_click()
