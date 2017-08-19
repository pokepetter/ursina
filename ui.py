from pandaeditor import *

class UI():

    def __init__(self):
        self.entity = None
        

    def fit_to_screen(self):
        screen_height = math.tan((math.pi / 180) * (40 * 1)) * distance(self.entity.getPos(render), camera.cam.getPos(render));
        self.entity.scale = (self.entity.scale[0] * screen_height * camera.aspect_ratio, self.entity.scale[1] * screen_height, 1)


    def input(self, key):
        if key == 'x':
            scene.clear()



# sys.modules[__name__] = UI()
