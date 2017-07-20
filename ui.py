from pandaeditor import *

class UI():

    def __init__(self):
        self.entity = None

    def fit_to_screen(self):
        screen_height = math.tan((math.pi / 180) * (40 * 1)) * distance(self.entity.node_path.getPos(render), camera.cam.getPos(render));
        aspect_ratio = screen_size[0] / screen_size[1]
        self.entity.scale = (self.entity.scale[0] * screen_height * aspect_ratio, 1, self.entity.scale[2] * screen_height)


    def input(self, key):
        if key == 'tab':
            # for c in self.entity.node_path.getChildren():
            #     print(c.entity.name)
            # self.entity.enabled = not self.entity.enabled
            load_scene('editor')

        if key == 'x':
            scene.clear()



# sys.modules[__name__] = UI()
