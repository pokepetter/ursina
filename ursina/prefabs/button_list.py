from ursina import *


class ButtonList(Entity):
    def __init__(self, button_dict, button_height=1.5, **kwargs):
        super().__init__(
        parent=camera.ui,
        model='quad',
        scale=(.5,.9),
        color=Button.color,
        origin=(-.5,.5),
        position=(-.25, .45),
        collider='box',
        )

        self.text_entity = Text(parent=self, origin=(-.5,.5), text='empty', world_scale=20, z=-.1, y=-.25*Text.size, x=.01)
        self.text_entity.line_height = button_height
        if button_height < 1.5:
            self.text_entity.y += .005

        self.button_height = self.text_entity.height

        self.button_dict = button_dict
        # self.actions = [*self.button_dict.values()] # gets set when setting button_dict
        self.highlight = Entity(parent=self, model='quad', color=color.white33, scale=(1,self.button_height), origin=(-.5,.5), z=-.01)

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def button_dict(self):
        return self._button_dict

    @button_dict.setter
    def button_dict(self, value):
        self._button_dict = value
        self.actions = [*self.button_dict.values()]
        self.text_entity.text = '\n'.join(self.button_dict.keys())


    def on_click(self):
        y = abs(int(self.highlight.y // self.button_height))
        action = self.actions[y]

        if callable(action):
            action()

        elif isinstance(action, Func):
            action.run()

        elif isinstance(action, Sequence):
            action.start()

        self.highlight.blink(color.black, .1)
        self.enabled = False


    def update(self):
        self.highlight.enabled = mouse.hovered_entity == self
        if mouse.hovered_entity == self:
            if abs(mouse.point[1] // self.button_height) > len(self.button_dict):
                self.highlight.enabled = False

            self.highlight.y = math.ceil(mouse.point[1] / self.button_height) * self.button_height



if __name__ == '__main__':
    app = Ursina()

    default = Func(print, 'not yet implemented')

    def test(a=1, b=2):
        print('------:', a, b)

    button_dict = {
        'one' :     None,
        'two' :     default,
        'tree' :    Func(test, 3, 4),
        'four' :    Func(test, b=3, a=4),
        'five':     Sequence(1, Func(print, 'lol'), loop=True),
    }
    for i in range(6, 25):
        button_dict[f'button {i}'] = Func(print, i)

    bl = ButtonList(button_dict)
    app.run()
