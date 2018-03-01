from pandaeditor import *


class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text()
        # self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        self.text.position = (-.5, .4)
        # self.text.align = 'top_left'
        self.text.scale *= 1
        self.text.text = '''
class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text()
        self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        self.text.position = (-.5, .4)
        # self.text.align = 'top_left'
        self.text.scale *= .1
        self.text.text = '<red>def <default>efefefefkejljwglij'''
        # self.t = InputField()

        # self.t = Text()

    # def input(self, key):
    #     print(key)
        self.indicator = Entity(model='quad', color=color.azure, scale=(.1, .1))
        self.indicator_origin = Entity(
            parent=self.indicator,
            model='quad',
            color=color.azure,
            origin=(0, -.5, -.1),
            scale=(.2, 5)
            )


# self.indicator.
    def input(self, key):
        if held_keys['left shift'] and key == 'a' or key == 'arrow left':
            self.indicator.x -= 1
            self.indicator.x = max(0, self.indicator.x)
        if held_keys['left shift'] and key == 'd' or key == 'arrow right':
            self.indicator.x += 1
            self.indicator.x = min(100, self.indicator.x)

if __name__ == '__main__':
    loadPrcFileData('', 'win-size 256 512')
    app = main.PandaEditor()
    # window.size = (256, 512)
    camera.orthographic = True
    camera.fov = 16
    window.color = color.color(0, 0, .1)
    window.fps_counter = False
    s = TextEditor()
    app.run()
