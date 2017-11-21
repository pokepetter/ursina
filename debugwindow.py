from pandaeditor import *


class DebugWindow():


    def __init___(self):
        self.b = load_prefab('editor_button')
        self.i = 0

    def write(self, s, message='default message'):
        # if not self.b:

        try:
            destroy(self.b)
        except:
            pass
        pass
        try:
            self.b = load_prefab('editor_button')
            self.b.scale_y = .025
            self.b.y = -.5
            self.b.origin = (0, -.5)
            self.b.text = str(message) + str(self.i)
            self.i += 1
        except:
            pass



    def flush(self):
        pass

sys.stdout = DebugWindow()
