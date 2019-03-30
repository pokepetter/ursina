from ursina import *
from ursina.internal_models.procedural.quad import Quad
import textwrap


class Button(Entity):

    color = color.black66

    def __init__(self, **kwargs):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui
        self.is_editor = False
        self.collision = True
        self.collider = 'box'

        for key, value in kwargs.items():   # set the scale before model for correct corners
            if key in ('scale', 'scale_x', 'scale_y', 'scale_z',
            'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):

                setattr(self, key, value)

        if not 'model' in kwargs:
            self.model = Quad(aspect=self.scale[0] / self.scale[1], subdivisions=4)
        self.color = Button.color

        self.text_entity = None
        self.disabled = False

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])
        self.original_color = self.color
        self.highlight_color = color.tint(self.original_color, .2)
        self.pressed_color = color.tint(self.original_color, -.2)

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def text(self):
        if self.text_entity:
            return self.text_entity.text

    @text.setter
    def text(self, value):
        if type(value) is str:
            if not self.text_entity:
                self.text_entity = Text(
                    parent = self,
                    size = Text.size * 20,
                    position = (-self.origin[0], -self.origin[1], -.1),
                    origin = (0,0)
                    )

            self.text_entity.text = value
            self.text_entity.world_scale = (1,1,1)


    def __setattr__(self, name, value):
        if name == 'color':
            # ignore setting original color if the button is modifying its own color on enter or on exit
            if not inspect.stack()[1][3] in ('__init__', 'on_mouse_enter', 'on_mouse_exit'):
                self.original_color = value
                self.highlight_color = color.tint(self.original_color, .2)
                self.pressed_color = color.tint(self.original_color, -.2)


        if name == 'origin':
            super().__setattr__(name, value)
            try:    # update collider position by making a new one
                self.collider = 'box'
                # self.text_entity.position = (-self.origin[0], -self.origin[1], -.1),
            except Exception as e:
                return e

        if name == 'on_click' and isinstance(value, str):
            object.__setattr__(self, 'on_click_string', textwrap.dedent(value))
            return

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e


    def input(self, key):
        if self.disabled:
            return

        if key == 'left mouse down':
            if self.hovered:
                self.color = self.pressed_color

        if key == 'left mouse up':
            if self.hovered:
                self.color = self.highlight_color


    def on_mouse_enter(self):
        if not self.disabled:
            self.color = self.highlight_color

        if hasattr(self, 'tooltip'):
            self.tooltip_scale = self.tooltip.scale
            self.tooltip.scale = (0,0,0)
            self.tooltip.enabled = True
            self.scale_animator = self.tooltip.animate_scale(self.tooltip_scale)


    def on_mouse_exit(self):
        if not self.disabled:
            self.color = self.original_color

        if hasattr(self, 'tooltip'):
            if hasattr(self, 'tooltip_scaler'):
                self.scale_animator.finish()
            self.tooltip.enabled = False

    def on_click(self):
        if self.disabled:
            return

        if hasattr(self, 'on_click_string'):
            exec(self.on_click_string)


    def fit(self):
        if not self.text_entity.text or self.text_entity.text == '':
            return

        self.text_entity.world_parent = scene
        self.scale = (
            (self.text_entity.width * Text.size * 2) + self.text_entity.height * Text.size * 2,
            self.text_entity.height * Text.size * 2 * 2
            )
        self.model = Quad(aspect=self.scale_x/self.scale_y)
        self.text_entity.world_parent = self
        print('fit t o text', self.scale)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # t = Test()
    # t.b.parent = scene
    # Button(scale=.3, text='hello world!', color=color.azure)
    b = Button(text='hello world!', color=color.azure, scale=.5)
    # b.fit()
    # EditorCamera()
    # b = Button(text='test\ntest', scale=(4,1), model='quad', collision=False)
    # b.text_entity.scale *= .5
    # t.b.tooltip = Text(text='yolo', background=True)
    app.run()
