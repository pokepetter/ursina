from ursina import Entity, Text, camera, color, mouse, BoxCollider, Sequence, Func, Vec2, Vec3, scene, Default, Audio
from ursina.models.procedural.quad import Quad
import textwrap

from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class Button(Entity):

    default_color = color.black90
    default_model = None # will default to rounded Quad

    def __init__(self, text='', parent=camera.ui, model=Default, radius=.1, origin=(0,0), text_origin=(0,0), text_size=1, color=Default, collider='box', highlight_scale=1, pressed_scale=1, disabled=False, **kwargs):
        super().__init__(parent=parent)

        for key in ('scale', 'scale_x', 'scale_y', 'scale_z', 'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):
            if key in kwargs:   # set the scale before model for correct corners
                setattr(self, key, kwargs[key])

        if model == Default:
            if not Button.default_model:
                if self.scale[0] != 0 and self.scale[1] != 0:
                    self.model = Quad(aspect=self.scale[0] / self.scale[1], radius=radius)
            else:
                self.model = Button.default_model
        else:
            self.model = model

        self.origin = origin

        if color == Default:
            color = Button.default_color
        self.color = color

        self.highlight_color = self.color.tint(.2)
        self.pressed_color = self.color.tint(-.2)
        self.highlight_scale = highlight_scale    # multiplier
        self.pressed_scale = pressed_scale     # multiplier
        self.highlight_sound = None
        self.pressed_sound = None
        self.collider = collider
        self.disabled = disabled

        self.text_entity = None
        self.text_origin = text_origin
        if text:
            self.text = text
            self.text_size = text_size

        for key, value in kwargs.items():
            setattr(self, key, value)


    def text_getter(self):
        if self.text_entity:
            return self.text_entity.text
        return ''

    def text_setter(self, value):
        if not isinstance(value, str):
            raise TypeError('Text must be a string')

        if not self.text_entity:
            self.text_entity = Text(text=value, parent=self.model, position=Vec3(self.text_origin[0],self.text_origin[1],-.01), origin=self.text_origin, add_to_scene_entities=False)
            self.text_entity.world_parent = self
            self.text_entity.world_scale = Vec3(20 * self.text_size)

        else:
            self.text_entity.text = value


    def text_origin_getter(self):
        if self.text_entity:
            return self.text_entity.origin

        return getattr(self, '_text_origin', (0,0))

    def text_origin_setter(self, value):
        self._text_origin = value
        if not self.text_entity:
            return

        self.text_entity.origin = value
        self.text_entity.world_parent = self.model
        self.text_entity.position = value
        # self.text_entity.x += self.model.radius * self.scale_y/self.scale_x * (-value[0]*2)
        # self.text_entity.y += self.model.radius * self.scale_y/self.scale_x * (-value[1]*2)
        self.text_entity.origin = value
        self.text_entity.world_parent = self

    def text_color_getter(self):
        return self.text_entity.color

    def text_color_setter(self, value):
        self.text_entity.color = value

    def icon_getter(self):
        return getattr(self, 'icon_entity', None)

    def icon_setter(self, value):
        if value and not hasattr(self, 'icon_entity'):
            self.icon_entity = Entity(parent=self.model, name=f'button_icon_entity_{value}', model='quad', z=-.1, add_to_scene_entities=False)
        self.icon_entity.texture = value
        longest_side = max(self.icon_entity.texture.width, self.icon_entity.texture.height)
        aspect_ratio = self.icon_entity.texture.width / self.icon_entity.texture.height
        if aspect_ratio == 1:
            return

        if self.icon_entity.texture.width < self.icon_entity.texture.height:
            self.icon_entity.scale_x = self.icon_entity.scale_y * aspect_ratio
        else:
            self.icon_entity.scale_y = self.icon_entity.scale_x / aspect_ratio


    def icon_world_scale_getter(self):
        if not self.icon:
            return None
        return self.icon_entity.world_scale

    def icon_world_scale_setter(self, value):
        if self.icon:
            self.icon_entity.world_scale = value

    def text_size_getter(self):
        return getattr(self, '_text_size', 1)

    def text_size_setter(self, value):
        self._text_size = value
        if self.text_entity:
            self.text_entity.world_scale = Vec3(value * 20)


    def origin_getter(self):
        return getattr(self, '_origin', Vec3.zero)

    def origin_setter(self, value):
        if hasattr(self, 'text_entity') and self.text_entity:
            self.text_entity.world_parent = self.model
            super().origin_setter(value)
            self.text_entity.world_parent = self
        else:
            super().origin_setter(value)

        if isinstance(self.collider, BoxCollider):    # update collider position by making a new one
            self.collider = 'box'



    def input(self, key):
        if self.disabled or not self.model:
            return

        if key == 'left mouse down':
            if self.hovered:
                self.model.setColorScale(self.pressed_color)
                self.model.setScale(Vec3(self.pressed_scale, self.pressed_scale, 1))
                if self.pressed_sound:
                    if isinstance(self.pressed_sound, Audio):
                        self.pressed_sound.play()
                    elif isinstance(self.pressed_sound, str):
                        Audio(self.pressed_sound, auto_destroy=True)

        if key == 'left mouse up':
            if self.hovered:
                self.model.setColorScale(self.highlight_color)
                self.model.setScale(Vec3(self.highlight_scale, self.highlight_scale, 1))
            else:
                self.model.setColorScale(self.color)
                self.model.setScale(Vec3(1,1,1))


    def on_mouse_enter(self):
        if not self.disabled and self.model:
            self.model.setColorScale(self.highlight_color)

            if self.highlight_scale != 1:
                self.model.setScale(Vec3(self.highlight_scale, self.highlight_scale, 1))

            if self.highlight_sound:
                if isinstance(self.highlight_sound, Audio):
                    self.highlight_sound.play()
                elif isinstance(self.highlight_sound, str):
                    Audio(self.highlight_sound, auto_destroy=True)

        if hasattr(self, 'tooltip') and self.tooltip:
            self.tooltip.enabled = True


    def on_mouse_exit(self):
        if not self.disabled and self.model:
            self.model.setColorScale(self.color)

            if not mouse.left and self.highlight_scale != 1:
                self.model.setScale(Vec3(1,1,1))

        if hasattr(self, 'tooltip') and self.tooltip:
            self.tooltip.enabled = False


    def fit_to_text(self, radius=.1, padding=Vec2(Text.size*1.5, Text.size)):
        if not self.text_entity or not self.text_entity.text or self.text_entity.text == '':
            return

        self.text_entity.world_parent = scene
        self.original_parent = self.parent
        self.parent = self.text_entity
        self.scale = Vec2(self.text_entity.width*self.text_entity.world_scale_x, self.text_entity.height*self.text_entity.world_scale_y) * Text.size * 2
        # self.scale = Vec2(self.text_entity.width, self.text_entity.height) * Text.size * 2
        self.scale += Vec2(*padding)
        self.position += self.text_origin * self.scale.xy * .5

        self.model = Quad(aspect=self.scale_x/self.scale_y, radius=radius)
        self.parent = self.original_parent
        self.text_entity.world_parent = self



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    Button.default_color = color.red
    b = Button(model='quad', scale=.05, x=-.5, color=color.lime, text='text scale\ntest', text_size=.5, text_color=color.black)
    b.text_size = .5
    b.on_click = Sequence(Wait(.5), Func(print, 'aaaaaa'), )

    b = Button(parent=camera.ui, text='hello world!', scale=.25)
    Button.default_color = color.blue
    b = Button(text='hello world!', icon='sword', scale=.25, text_origin=(-.5,0), x=.5)
    # b.fit_to_text()
    b.on_click = application.quit # assign a function to the button.
    b.tooltip = Tooltip('exit')

    par = Entity(parent=camera.ui, scale=.2, y=-.2)
    b = Button(parent=par, text='test', scale_x=1, origin=(-.5,.5))
    b.text ='new text'
    print(b.text_entity)

    Button(text='sound', scale=.2, position=(-.25,-.2), color=color.pink, highlight_sound='blip_1', pressed_sound=Audio('coin_1', autoplay=False))

    # Entity(model='quad', parent=b, x=1)
    Text('Text size\nreference', x=.15)
    # b.eternal = True
    def input(key):

        if key == 'd':
            scene.clear()

        if key == 'space':
            b.text = 'updated text'


    app.run()
