from pandaeditor import *


class UI():

    def __init__(self):
        self.target = None

    def fit_to_screen(self):
        screen_height = math.tan((math.pi / 180) * (40 * 1)) * distance(self.target.node_path.getPos(render), camera.position);
        aspect_ratio = screen_size[0] / screen_size[1]
        self.target.scale = (self.target.scale[0] * screen_height * aspect_ratio, 1, self.target.scale[2] * screen_height)
