from ursina import *
from ursina.models.procedural.quad import Quad
import textwrap


class Button(Entity):

    color = color.black66

    def __init__(self, **kwargs):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui
        self.is_editor = False
        self.collider = 'box'

        for key, value in kwargs.items():   # set the scale before model for correct corners
            if key in ('scale', 'scale_x', 'scale_y', 'scale_z',
            'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):

                setattr(self, key, value)

        if not 'model' in kwargs and self.scale[0] != 0 and self.scale[1] != 0:
            self.model = Quad(aspect=self.scale[0] / self.scale[1], subdivisions=4)
        self.color = Button.color

        self.text_entity = None
        self.disabled = False

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])
        self.original_color = self.color
        self.highlight_color = color.tint(self.original_color, .2)
        self.pressed_color = color.tint(self.original_color, -.2)
        self.highlight_scale = 1    # multiplier
        self.pressed_scale = .9     # multiplier

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.original_scale = self.scale


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

    @property
    def text_origin(self):
        if not self.text_entity:
            return(0,0)

        return self.text_entity.origin

    @text_origin.setter
    def text_origin(self, value):
        if not self.text_entity:
            return

        self.text_entity.position = value
        self.text_entity.x += self.model.radius * self.scale_y/self.scale_x * (-value[0]*2)
        self.text_entity.y += self.model.radius * self.scale_y/self.scale_x * (-value[1]*2)
        self.text_entity.origin = value


    def __setattr__(self, name, value):
        if name == 'color':
            # ignore setting original color if the button is modifying its own color on enter or on exit
            if inspect.stack()[1].filename == __file__ and not inspect.stack()[1][3] == '__init__':
                return

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
                self.model.setScale(Vec3(self.pressed_scale, 1, self.pressed_scale))

        if key == 'left mouse up':
            if self.hovered:
                self.color = self.highlight_color
                self.model.setScale(Vec3(self.highlight_scale, 1, self.highlight_scale))
            else:
                self.color = self.original_color
                self.model.setScale(Vec3(1,1,1))


    def on_mouse_enter(self):
        if not self.disabled:
            self.color = self.highlight_color
            if self.highlight_scale != 1:
                self.scale = self.original_scale * self.highlight_scale

        if hasattr(self, 'tooltip'):
            self.tooltip_scale = self.tooltip.scale
            self.tooltip.scale = (0,0,0)
            self.tooltip.enabled = True
            self.scale_animator = self.tooltip.animate_scale(self.tooltip_scale)


    def on_mouse_exit(self):
        if not self.disabled:
            self.color = self.original_color
            if not mouse.left and self.highlight_scale != 1:
                self.scale = self.original_scale

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
        print('fit to text', self.scale)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # t = Test()
    # t.b.parent = scene
    # Button(scale=.3, text='hello world!', color=color.azure)
    # b = Button(text='hello world!', color=color.azure, scale=.05)
    class Yolo(Button):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.text = 'yolo'


    b = Button(text='button text', scale=(1.5,.1), text_origin=(-.5,0))

    # b.fit()
    # EditorCamera()
    # b = Button(text='test\ntest', scale=(4,1), model='quad', collision=False)
    # b.text_entity.scale *= .5
    # t.b.tooltip = Text(text='yolo', background=True)
    app.run()
