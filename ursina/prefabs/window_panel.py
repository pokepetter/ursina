from ursina import *
from ursina.prefabs.input_field import InputField


class Space():
    def __init__(self, height=1):
        self.height = height


class WindowPanel(Draggable):
    def __init__(self, title='', content=[], **kwargs):
        super().__init__(
            origin = (-0, .5),
            scale = (.5, Text.size),
            color = color.black,
            )

        # print(content)
        self.content = content
        self.text = title
        self.popup = False

        for key, value in kwargs.items():
            setattr(self, key ,value)

        if self.text_entity:
            self.text_entity.world_scale_y = 1

        if content:
            spacing = .5
            height = 1 + spacing

            if isinstance(content, dict):
                content = content.values()

            for c in content:
                # print('........', c)
                if isinstance(c, Space):
                    height += c.height

                if isinstance(c, Entity):
                    c.world_parent = self
                    c.y = -height
                    c.z = 0


                    if isinstance(c, Text):
                        c.origin = (-.5, .5)
                        c.x = -.48
                        height += len(c.lines)

                    elif isinstance(c, Button):
                        c.world_parent = self
                        c.scale = (.98, 2)
                        if hasattr(c, 'height'):
                            c.scale_y = height
                        c.model = Quad(aspect=c.world_scale_x/c.world_scale_y)
                        height += c.scale_y
                        c.y -= c.scale_y/2

                    elif hasattr(c, 'scale_y'):
                        height += c.scale_y

                    if hasattr(c, 'text_entity') and c.text_entity is not None:
                        c.text_entity.world_scale = (1,1,1)

                    height += spacing

            self.panel = Panel(parent=self, scale_y=height, model=Quad(), origin=(0, .5), z=.1, color=self.color.tint(.1))
            self.panel.model = Quad(aspect=self.panel.world_scale_x/self.panel.world_scale_y, radius=.025)
            self.panel.origin = (0, .5)


        if self.popup:
            self.lock_x = True
            self.lock_y = True
            self.bg = Button(
                parent=self,
                z=.1,
                scale=(999, 999),
                color=color.black66,
                highlight_color=color.black66,
                pressed_color=color.black66,
                )

            def close():
                self.bg.enabled = False
                self.animate_scale_y(0, duration=.1)
                invoke(setattr, self, 'enabled', False, delay=.2)

                if hasattr(self, 'close'):
                    self.close()

            self.bg.on_click = close


if __name__ == '__main__':
    app = Ursina()
    WindowPanel(
        title='Custom Window',
        content=(
            Text('leflaijfae\njofeoijfw'),
            Button(text='test', color=color.green),
            Space(height=1),
            Text('leflaijfae\njofeoijfw'),
            InputField()
            # ButtonGroup(('test', 'eslk', 'skffk'))
            )
        )
    # Text(dedent('''
    # [        My Window            [x]]
    # | Create your character
    # |
    # | InputField
    # | [[Male][Female][Other]]
    # | ButtonGroup(('male', 'female', 'other'))
    # | Option1:  [t]   Option2: []
    # |
    # |[      Submit     ] [ Clear ]
    # '''[1:]), font='VeraMono.ttf', origin=(0,0)
    # )
    # WindowPanel(title='My Window', (
    #     Text('Enter Name:'),
    #     InputField('name'),
    #     (
    #         Button(text='Submit', on_click='save_system.save(self.parent.input_field.value)'),
    #         Button(text='Clear', on_click='self.parent.input_field.value='')')
    #         )
    #     ))
    app.run()
