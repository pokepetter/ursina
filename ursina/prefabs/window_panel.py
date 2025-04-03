from ursina import Entity, Draggable, Text, Slider, Button, color, Vec3, Quad, invoke
from ursina.prefabs.input_field import InputField


class Space():
    def __init__(self, height=1):
        self.height = height


class WindowPanel(Draggable):
    def __init__(self, title='', content=[], **kwargs):
        self.content = content
        self.popup = False
        self._prev_input_field = None
        super().__init__(origin=(-0,.5), scale=(.5, .05), text=title, color=color.black)
        self._original_scale = self.scale

        for key, value in kwargs.items():
            setattr(self, key ,value)

        self.panel = Entity(parent=self, model='quad', origin=(0,.5), z=.1, color=self.color.tint(.1), collider='box')

        if self.popup:
            self.lock = Vec3(1,1,1)
            self.bg = Button(parent=self, z=1, scale=(999, 999), color=color.black66, highlight_color=color.black66, pressed_color=color.black66)
            self.bg.on_click = self.disable

        if self.content:
            self.layout()


    def layout(self):
        content = self.content
        if not content:
            return
        spacing = .25
        height = 1.5 + spacing

        if isinstance(content, dict):
            content = content.values()

        for c in content:
            # print('........', c)
            if isinstance(c, Space):
                height += c.height

            if isinstance(c, Entity):
                c.world_parent = self
                c.position = (0, -height, 0)

                if isinstance(c, InputField):
                    c.text_field.text_entity.world_scale = Vec3(20,20,1)
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
                    # print('-------------', c.scale_y * c.height)
                    height += 1

                elif hasattr(c, 'scale_y'):
                    height += c.scale_y

                if hasattr(c, 'text_entity') and c.text_entity is not None:
                    c.text_entity.world_scale = Vec3(20,20,1)

                height += spacing

        self.panel.scale_y = height
        self.panel.model = Quad(aspect=self.panel.world_scale_x/self.panel.world_scale_y, radius=.025)
        self.panel.origin = (0, .5)



if __name__ == '__main__':
    '''
    WindowPanel is an easy way to create UI. It will automatically layout the content.
    '''
    from ursina import Ursina, ButtonGroup
    app = Ursina()
    wp = WindowPanel(
        title='Custom Window',
        content=(
            Text('Name:'),
            InputField(name='name_field'),
            Button(text='Submit', color=color.azure),
            Slider(),
            Slider(),
            ButtonGroup(('test', 'eslk', 'skffk'))
            ),
        popup=True
        )
    wp.y = wp.panel.scale_y / 2 * wp.scale_y    # center the window panel
    wp.layout()

    def input(key):
        if key == 'space':
            wp.enabled = True

    app.run()
