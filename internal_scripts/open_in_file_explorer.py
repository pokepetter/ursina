import sys
sys.path.append("..")
from pandaeditor import *
import subprocess

class OpenInFileExplorer():

    # def __init__(self):
    #     self.path = 'afafaf'

    def input(self, key):
        if key == 'right mouse down' and self.entity.hovered:
            print('yoooooo', os.name, 'explorer "' + self.path + '"')
            if os.name == 'nt':
                subprocess.Popen('explorer "' + self.path + '"')
