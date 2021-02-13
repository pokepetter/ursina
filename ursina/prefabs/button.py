from ursina import *
from ursina.models.procedural.quad import Quad
import textwrap


class Button(Entity):

    color = color.black66
    default_model = None # will deatult to rounded Quad

    def __init__(self, text='', **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.collider = 'box'
        self.disabled = False
        self._on_click = None

        for key, value in kwargs.items():   # set the scale before model for correct corners
            if key in ('scale', 'scale_x', 'scale_y', 'scale_z',
            'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):

                setattr(self, key, value)

        if Button.default_model is None:
            if not 'model' in kwargs and self.scale[0] != 0 and self.scale[1] != 0:
                self.model = Quad(aspect=self.scale[0] / self.scale[1], subdivisions=4)
        else:
            self.model = Button.default_model
        self.color = Button.color

        self.text_entity = None
        if text:
            self.text = text

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])
        self.highlight_color = self.color.tint(.2)
        self.pressed_color = self.color.tint(-.2)
        self.highlight_scale = 1    # multiplier
        self.pressed_scale = 1     # multiplier

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.original_scale = self.scale
        if self.text_entity != None:
            self.text_entity.world_scale = 1

        self.icon = None


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
                    origin = (0,0),
                    add_to_scene_entities = False,
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


    @property
    def icon(self):
        return self.icon_entity

    @icon.setter
    def icon(self, value):
        if value:
            if not hasattr(self, 'icon_entity'):
                self.icon_entity = Entity(parent=self.model, name=f'buttonicon_entity_{value}', model='quad', texture=value, z=-.1, add_to_scene_entities=False)
            else:
                self.icon_entity.texture = value


    def __setattr__(self, name, value):
        if name == 'color':
            try:
                self.highlight_color = value.tint(.2)
                self.pressed_color = value.tint(-.2)
            except:
                pass

        if name == 'origin':
            if hasattr(self, 'text_entity') and self.text_entity:
                self.text_entity.world_parent = self.model
                super().__setattr__(name, value)
                self.text_entity.world_parent = self
            else:
                super().__setattr__(name, value)

            if isinstance(self.collider, BoxCollider):    # update collider position by making a new one
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


    def input(self, key):
        if self.disabled or not self.model:
            return

        if key == 'left mouse down':
            if self.hovered:
                self.model.setColorScale(self.pressed_color)
                self.model.setScale(Vec3(self.pressed_scale, 1, self.pressed_scale))

        if key == 'left mouse up':
            if self.hovered:
                self.model.setColorScale(self.highlight_color)
                self.model.setScale(Vec3(self.highlight_scale, 1, self.highlight_scale))
            else:
                self.model.setColorScale(self.color)
                self.model.setScale(Vec3(1,1,1))


    def on_mouse_enter(self):
        if not self.disabled and self.model:
            self.model.setColorScale(self.highlight_color)

            if self.highlight_scale != 1:
                self.model.setScale(Vec3(self.highlight_scale, 1, self.highlight_scale))

        if hasattr(self, 'tooltip'):
            self.tooltip.scale = (0,0,0)
            self.tooltip.enabled = True
            self.tooltip.animate_scale(self.tooltip.original_scale)


    def on_mouse_exit(self):
        if not self.disabled and self.model:
            self.model.setColorScale(self.color)

            if not mouse.left and self.highlight_scale != 1:
                self.model.setScale(Vec3(1,1,1))

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


    def fit_to_text(self, radius=.1):
        if not self.text_entity.text or self.text_entity.text == '':
            return

        self.text_entity.world_parent = scene
        self.scale = (
            (self.text_entity.width * Text.size * 2) + self.text_entity.height * Text.size * 2,
            self.text_entity.height * Text.size * 2 * 2
            )
        self.model = Quad(aspect=self.scale_x/self.scale_y, radius=radius)
        self.text_entity.world_parent = self
        # print('fit to text', self.scale)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    b = Button(text='hello world!', color=color.azure, icon='sword', scale=.25, text_origin=(-.5,0))
    # b.fit_to_text()
    b.on_click = application.quit # assign a function to the button.
    b.tooltip = Tooltip('exit')

    app.run()
