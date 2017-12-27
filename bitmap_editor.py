from pandaeditor import *


class BitmapEditor(Entity):

    def __init__(self):
        super().__init__()
        # self.file =
        self.display()
        self.scale *= 1/16

    def display(self):
        print('display')
        for y in range(32):
            for x in range(32):
                p = Button()
                p.parent = self
                # p.add_script(Pixel())
                p.scripts.append(Pixel())
                p.position = (x, y)

class Pixel():
    def on_click(self):
        self.entity.color = color.orange


if __name__ == '__main__':
    app = PandaEditor()
    height = window.screen_resolution[1] / 2
    window.size = (height, height)
    print(camera.aspect_ratio)
    # window.position = (10, 10)
    scene.entity = BitmapEditor()
    app.run()
