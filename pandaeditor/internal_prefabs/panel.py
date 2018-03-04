from pandaeditor import *

class Panel(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'panel'
        self.parent = scene.ui
        self.model = 'quad'
        self.color = color.panda_button

if __name__ == '__main__':
    app = PandaEditor()
    p = Panel()
    app.run()
