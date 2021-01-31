from ursina import *


class ButtonList(Entity):
    def __init__(self, button_dict, button_height=1.365, fit_height=True, width=.5, **kwargs):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(width,.9),
            color=Button.color,
            origin=(-.5,.5),
            position=(-.25, .45),
            collider='box',
        )
        self.fit_height = fit_height
        self.button_height = button_height
        if fit_height:
            self.scale_y = button_height * len(button_dict) * Text.size

        self.text_entity = Text(parent=self, origin=(-.5,.5), text='empty', world_scale=20, z=-.1, x=.01)
        self.text_entity.line_height = button_height
        self.text_entity.world_y -= .15

        self.button_height = self.text_entity.height

        self.button_dict = button_dict
        # self.actions = [*self.button_dict.values()] # gets set when setting button_dict
        self.highlight = Entity(parent=self, model='quad', color=color.white33, scale=(1,self.button_height), origin=(-.5,.5), z=-.01, add_to_scene_entities=False)
        self.selection_marker = Entity(parent=self, model='quad', color=color.azure, scale=(1,self.button_height), origin=(-.5,.5), z=-.02, enabled=False, add_to_scene_entities=False)

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


    def input(self, key):
        # handle click here instead of in on_click so you can assign a custom on_click function
        if key == 'left mouse down' and self.hovered:
            y = round(abs(self.highlight.y / self.button_height))

            action = self.actions[y]
            self.highlight.blink(color.black, .1)
            self.selection_marker.enabled = True
            self.selection_marker.y = self.highlight.y

            if callable(action):
                action()

            elif isinstance(action, Sequence):
                action.start()

        if key == 'left mouse down' and not self.hovered:
            self.selection_marker.enabled = False


    def update(self):
        self.highlight.enabled = mouse.hovered_entity == self
        if mouse.hovered_entity == self:
            if abs(mouse.point[1] // self.button_height) > len(self.button_dict):
                self.highlight.enabled = False

            self.highlight.y = ceil(mouse.point[1] / self.button_height) * self.button_height


    def on_disable(self):
        self.selection_marker.enabled = False




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
        # 'five':     Sequence(1, Func(print, 'lol'), loop=True),
    }
    for i in range(6, 12):
        button_dict[f'button {i}'] = Func(print, i)

    bl = ButtonList(button_dict, fit_height=True)
    # bl.scale *= .2
    bl.on_click = Func(setattr, bl, 'enabled', False)

    # bl.button_dict = {'a':Func(print,'lodlw'), 'b':1, 'c':1}
    app.run()
