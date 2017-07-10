from pandaeditor import *


class UI():

    def __init__(self):
        self.gameobject = None

    def fit_to_screen(self):
        screen_height = math.tan((math.pi / 180) * (40 * 1)) * distance(self.gameobject.node_path.getPos(render), camera.cam.getPos(render));
        aspect_ratio = screen_size[0] / screen_size[1]
        self.gameobject.scale = (self.gameobject.scale[0] * screen_height * aspect_ratio, 1, self.gameobject.scale[2] * screen_height)
