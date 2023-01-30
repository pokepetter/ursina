from ursina import Entity, Text, camera, Button, color, mouse, Sequence
from math import floor


class ButtonList(Entity):
    def __init__(self, button_dict, button_height=1.1, width=.5, font=Text.default_font, **kwargs):
        super().__init__(parent=camera.ui, position=(-(width/2), .45))

        self.button_height = button_height
        self.width = width
        self.text_entity = Text(parent=self, font=font, origin=(-.5,.5), text='empty', world_scale=20, z=-.1, x=.01, y=-(button_height*.25*Text.size), line_height=button_height)
        self.bg = Entity(parent=self, model='quad', origin=(-.5,.5), scale=width, color=Button.color, collider='box')
        self.highlight = Entity(parent=self.bg, model='quad', color=color.white33, scale=(1,self.button_height), origin=(-.5,.5), z=-.01, add_to_scene_entities=False)
        self.selection_marker = Entity(parent=self.bg, model='quad', color=color.azure, scale=(1,self.button_height), origin=(-.5,.5), z=-.02, enabled=False, add_to_scene_entities=False)
        self.button_dict = button_dict

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def button_dict(self):
        return self._button_dict

    @button_dict.setter
    def button_dict(self, value):
        self._button_dict = value
        self.actions = list(self._button_dict.values())
        self.bg.scale_y = self.button_height * len(value) * Text.size
        self.text_entity.text = '\n'.join(self.button_dict.keys())
        self.text_entity.line_height = self.button_height
        self.highlight.scale_y = 1 / len(value)
        self.selection_marker.scale_y = 1 / len(value)


    def input(self, key):
        # handle click here instead of in on_click so you can assign a custom on_click function
        if key == 'left mouse down' and self.bg.hovered:
            y = floor(-mouse.point.y * len(self.button_dict))

            action = self.actions[y]
            self.highlight.blink(color.black, .1)
            self.selection_marker.enabled = True
            self.selection_marker.y = self.highlight.y

            if callable(action):
                action()

            elif isinstance(action, Sequence):
                action.start()

        if key == 'left mouse down' and not self.bg.hovered:
            self.selection_marker.enabled = False


    def update(self):
        self.highlight.enabled = mouse.hovered_entity == self.bg
        if mouse.hovered_entity == self.bg:
            y = floor(-mouse.point.y * len(self.button_dict))
            self.highlight.y = -y / len(self.button_dict)


    def on_disable(self):
        self.selection_marker.enabled = False




if __name__ == '__main__':
    from ursina import Ursina, Func
    app = Ursina()

    default = Func(print, 'not yet implemented')

    def test(a=1, b=2):
        print('------:', a, b)

    button_dict = {}
    for i in range(6, 20):
        button_dict[f'button {i}'] = Func(print, i)

    bl = ButtonList(button_dict, font='VeraMono.ttf', button_height=1.5)
    def input(key):
        if key == 'space':
            bl.button_dict = {
                'one' :     None,
                'two' :     default,
                'tree' :    Func(test, 3, 4),
                'four' :    Func(test, b=3, a=4),
            }

    app.run()
