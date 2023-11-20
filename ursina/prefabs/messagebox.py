from ursina import Entity, Button, Text, camera, color, mouse, BoxCollider, Sequence, Vec2, Vec3, scene, held_keys, \
    destroy
from ursina.models.procedural.quad import Quad
import textwrap


class MessageBox(Entity):
    color = color.black66
    default_model = None  # will default to rounded Quad

    def __init__(self, messagebox_name='', text='', radius=.005, scale=(.8, .5), **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.disabled = False
        self._on_click = None

        for key, value in kwargs.items():  # set the scale before model for correct corners
            if key in ('scale', 'scale_x', 'scale_y', 'scale_z',
                       'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):
                setattr(self, key, value)

        if MessageBox.default_model is None:
            if not 'model' in kwargs and self.scale[0] != 0 and self.scale[1] != 0:
                self.model = Quad(aspect=self.scale[0] / self.scale[1], radius=radius, scale=scale)
        else:
            self.model = MessageBox.default_model
        self.color = MessageBox.color

        self.text_entity = None
        if text:
            self.text = text

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])
        self.highlight_color = self.color.tint(.2)
        self.pressed_color = self.color.tint(-.2)
        self.highlight_scale = 1  # multiplier
        self.pressed_scale = 1  # multiplier
        self.collider = 'box'

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.original_scale = self.scale
        if self.text_entity is not None:
            self.text_entity.world_scale = 1

        self.exit_button = Button(parent=self, eternal=True, radius=.25,ignore_paused=True, origin=(0, 0, 2),
                                  position=(.36, .225), z=1, scale=(.05, .025), color=color.red.tint(-.2), text='x')

        self.bar = Button(parent=self, eternal=True, ignore_paused=True, origin=(0, 0, 1),
                          position=(0, .225), z=1, scale=(.8, .05), color=color.white, name='bar')

        self.title = Text(parent=self, text=messagebox_name, size=Text.size * 20, color=color.black,
                          position=(-.30, .225, -.1), origin=(0, 0),
                          add_to_scene_entities=False)

        def _exit_button_input(key):
            destroy(self)

        self.exit_button.input = _exit_button_input

    @property
    def text(self):
        if self.text_entity:
            return self.text_entity.text

    @text.setter
    def text(self, value):
        if type(value) is str:
            if not self.text_entity:
                self.text_entity = Text(parent=self, size=Text.size * 20,
                                        position=(-self.origin[0], -self.origin[1], -.1), origin=(0, 0),
                                        add_to_scene_entities=False)

            self.text_entity.text = value
            self.text_entity.world_scale = (1, 1, 1)

    @property
    def text_origin(self):
        if not self.text_entity:
            return 0, 0

        return self.text_entity.origin

    @text_origin.setter
    def text_origin(self, value):
        if not self.text_entity:
            return

        self.text_entity.world_parent = self.model
        self.text_entity.position = value
        # self.text_entity.x += self.model.radius * self.scale_y/self.scale_x * (-value[0]*2)
        # self.text_entity.y += self.model.radius * self.scale_y/self.scale_x * (-value[1]*2)
        self.text_entity.origin = value
        self.text_entity.world_parent = self

    @property
    def text_color(self):
        return self.text_entity.color

    @text_color.setter
    def text_color(self, value):
        self.text_entity.color = value

    def __setattr__(self, name, value):
        if name == 'origin':
            if hasattr(self, 'text_entity') and self.text_entity:
                self.text_entity.world_parent = self.model
                super().__setattr__(name, value)
                self.text_entity.world_parent = self
            else:
                super().__setattr__(name, value)

            if isinstance(self.collider, BoxCollider):  # update collider position by making a new one
                self.collider = 'box'

        if name == 'on_click':
            self._on_click = value

            if isinstance(value, Sequence):
                value.auto_destroy = False
            return

        if name == 'eternal':
            try:
                self.text_entity.eternal = value
            except:
                pass
        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e

    def on_mouse_enter(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.enabled = True

    def on_mouse_exit(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.enabled = False

    def on_click(self):
        if self.disabled:
            return

        action = self._on_click
        if callable(action):
            action()

        elif isinstance(action, Sequence):
            action.start()

        elif isinstance(action, str):
            exec(textwrap.dedent(action))

    def fit_to_text(self, radius=.1, padding=Vec2(Text.size * 1.5, Text.size)):
        if not self.text_entity.text or self.text_entity.text == '':
            return

        self.text_entity.world_parent = scene
        self.original_parent = self.parent
        self.parent = self.text_entity
        self.scale = Vec2(self.text_entity.width, self.text_entity.height) * Text.size * 2
        self.scale += Vec2(*padding)

        self.model = Quad(aspect=self.scale_x / self.scale_y, radius=radius)
        self.parent = self.original_parent
        self.text_entity.world_parent = self


if __name__ == '__main__':
    from ursina import Ursina, Tooltip

    app = Ursina()
    b = MessageBox(messagebox_name='My Messagebox', text='hello world!', scale=(.8, .5), color=color.azure, text_origin=(-.36, .18))
    b.tooltip = Tooltip("MessageBox")

    app.run()
