import sys
from pandaeditor import *

class ExitButton():

    def on_click(self):
        os._exit(0)


    def input(self, key):
        if key == 'q':
            self.on_click()
