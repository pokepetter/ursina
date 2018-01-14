from pandaeditor import *


class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        # self.text = Text()
        # self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        # self.text.scale
        # self.text.text = 'efefefefkejljwglij'
        self.t = InputField()

        # self.t = Text()

    # def input(self, key):
    #     print(key)

if __name__ == '__main__':
    loadPrcFileData('', 'win-size 256 512')
    app = main.PandaEditor()
    # window.size = (256, 512)
    window.fps_counter = False
    s = TextEditor()
    app.run()
