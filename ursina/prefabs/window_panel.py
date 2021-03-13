from ursina import *
from ursina.prefabs.input_field import InputField


class Space():
    def __init__(self, height=1):
        self.height = height


class WindowPanel(Draggable):
    def __init__(self, title='', content=[], **kwargs):
        super().__init__(origin=(-0,.5), scale=(.5, Text.size*2), color=color.black)

        self.content = content
        self.text = title
        self.popup = False
        self._prev_input_field = None
        self._original_scale = self.scale

        for key, value in kwargs.items():
            setattr(self, key ,value)

        if self.text_entity:
            self.text_entity.world_scale_y = 1

        if content:
            spacing = .25
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

                    if isinstance(c, InputField):
                        if self._prev_input_field:
                            self._prev_input_field.next_field = c
                        self._prev_input_field = c

                    if isinstance(c, Text):
                        c.origin = (-.5, .5)
                        c.x = -.48
                        height += len(c.lines)

                    elif isinstance(c, Button):
                        c.world_parent = self
                        c.scale = (.9, 1)
                        if hasattr(c, 'height'):
                            c.scale_y = height
                        c.model = Quad(aspect=c.world_scale_x/c.world_scale_y)
                        height += c.scale_y
                        # c.y -= c.scale_y/2

                    elif isinstance(c, Slider):
                        c.world_parent = self
                        c.x = -.5 * .9
                        c.scale = (.9*2, 20)
                        print('-------------', c.scale_y * c.height)
                        height += 1

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

            self.bg.on_click = self.close


    def on_enable(self):
        if self.popup:
            self.bg.enabled = True
            self.animate_scale(self._original_scale, duration=.1)


    def close(self):
        if self.popup:
            self.bg.enabled = False
        self.animate_scale_y(0, duration=.1)
        invoke(setattr, self, 'enabled', False, delay=.2)


if __name__ == '__main__':
    '''
    WindowPanel is an easy way to create UI. It will automatically layout the content.
    '''
    app = Ursina()
    WindowPanel(
        title='Custom Window',
        content=(
            Text('Name:'),
            InputField(name='name_field'),
            # Text('Age:'),
            # InputField(name='age_field'),
            # Text('Phone Number:'),
            # InputField(name='phone_number_field'),
            # Space(height=1),
            # Text('Send:'),
            Button(text='Submit', color=color.azure),
            Slider(),
            Slider(),
            # ButtonGroup(('test', 'eslk', 'skffk'))
            ),
            # popup=True
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
