from ursina import *


class InputField(Button):

    def __init__(self, text='...', **kwargs):
        super().__init__(
            scale=(.5, Text.size * 2),
            highlight_scale = 1,
            pressed_scale = 1,
            )
        self.editing = False
        self.text = text
        self.start_text = self.text

        if self.text:
            self.text_entity.color = color.gray
        self.multiline = False
        self.t = 0

        for key, value in kwargs.items():
            setattr(self, key, value)


    def _get_text(self):
        if not self.text_entity:
            return ''

        if self.editing and self.text_entity.text.endswith('|'):
            return self.text_entity.text[:-1]

        return self.text_entity.text

    text = property(_get_text, Button.text.__set__)


    def update(self):
        if self.editing:
            self.t += time.dt
            if self.t >= .5:
                if not self.text_entity.text.endswith('|'):
                    self.text_entity.text += '|'
                else:
                    self.text_entity.text = self.text_entity.text[:-1]
                self.t = 0


    def input(self, key):
        super().input(key)

        if key == 'left mouse down':
            print(self.hovered)
            self.editing = self.hovered

            if self.editing:
                self.text_entity.color = color.text_color
                if self.text in (self.start_text, self.start_text+'|'):
                    self.text = ''
            else:
                self.text_entity.color = color.gray
                if self.text.endswith('|'):
                    self.text = self.text[:-1]

        if not self.editing:
            return

        if self.text.endswith('|'):
            self.text = self.text[:-1]

        if len(key) == 1 and key != '\n':
            if held_keys['shift']:
                self.text += key.upper()
            else:
                self.text += key
            # print('adding:', key)

        if key == 'shift--':
            self.text += '_'

        if key == 'space':
            self.text += ' '

        if key == 'backspace':
            if not held_keys['control']:
                if len(self.text) == 1:
                    self.text = ''
                    return

                self.text = self.text[:-1]
            else:
                if ' ' in self.text:
                    self.text = self.text.rsplit(' ')[0]
                else:
                    self.text = ''

        if key == 'enter':
            if self.multiline:
                self.text += '\n'

            elif held_keys['shift']:
                self.editing = False


if __name__ == '__main__':
    app = Ursina()

    test = InputField()
    Entity(model='quad', scale=.02, color=color.red)

    app.run()
