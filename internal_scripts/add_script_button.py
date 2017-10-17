import sys
sys.path.append("..")
from pandaeditor import *

class AddScriptButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                scene.editor.selection[0].add_script(os.path.basename(self.path)[:-3])
                print('scripts:', scene.editor.selection[0].scripts)
