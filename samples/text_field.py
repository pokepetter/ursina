from ursina import *

class TextField(Entity):

    def __init__(self):
        super().__init__()
        self.edit_button = Button(parent=self)
        self.edit_button.scale *= .2
        self.edit_button.model = Circle()
        self.edit_button.color = color.orange
        self.edit_button.on_click = '''self.parent.editing = True'''

        self.text_entity = Text('Yolo')
        self.text_entity.wordwrap = 20
        self.editing = False

    @property
    def editing(self):
        return self._editing

    @editing.setter
    def editing(self, value):
        self._editing = value
        print(value)
        self.edit_button.enabled = not value

    def input(self, key):
        if self.editing:
            if len(key) == 1:
                self.text_entity.text += key

            if key == 'space':
                self.text_entity.text += ' '
            self.text_entity.wordwrap = 40
            self.text_entity.background = True
            # if key == 'enter'


if __name__ == '__main__':
    app = Ursina()
    TextField()
    # window.color = color.blue
    app.run()
