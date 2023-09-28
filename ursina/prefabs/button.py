from ursina import Entity, Text, camera, color, mouse, BoxCollider, Sequence, Func, Vec2, Vec3, scene
from ursina.models.procedural.quad import Quad
import textwrap

from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class Button(Entity):

    default_color = color.black90
    default_model = None # will default to rounded Quad

    def __init__(self, text='', radius=.1, text_origin=(0,0), **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.disabled = False

        for key, value in kwargs.items():   # set the scale before model for correct corners
            if key in ('scale', 'scale_x', 'scale_y', 'scale_z',
            'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z'):

                setattr(self, key, value)

        if Button.default_model is None:
            if not 'model' in kwargs and self.scale[0] != 0 and self.scale[1] != 0:
                self.model = Quad(aspect=self.scale[0] / self.scale[1], radius=radius)
        else:
            self.model = Button.default_model

        if 'color' in kwargs:
            self.color = kwargs['color']
        else:
            self.color = Button.default_color

        self.highlight_color = self.color.tint(.2)
        self.pressed_color = self.color.tint(-.2)
        self.highlight_scale = 1    # multiplier
        self.pressed_scale = 1     # multiplier
        self.collider = 'box'


        self.text_entity = None
        if text:
            self.text = text

        self.text_origin = text_origin
        self.original_scale = self.scale

        for key, value in kwargs.items():
            setattr(self, key, value)
        # if 'eternal' in kwargs: # eternal needs to be set after text, so the text_Entity also gets the same eternal value
        #     self.eternal = kwargs['eternal']


    def text_getter(self):
        if self.text_entity:
            return self.text_entity.text

    def text_setter(self, value):
        if isinstance(value, str) and not self.text_entity:
            self.text_entity = Text(parent=self, size=Text.size*20, position=(-self.origin[0],-self.origin[1],-.1), origin=(0,0), add_to_scene_entities=False)

        self.text_entity.text = value
        self.text_entity.world_scale = Vec3(self.text_size)


    def text_origin_getter(self):
        if not self.text_entity:
            return (0,0)
        return self.text_entity.origin

    def text_origin_setter(self, value):
        if not self.text_entity:
            return

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
        return self.getattr('icon_entity', None)

    def icon_setter(self, value):
        if value and not hasattr(self, 'icon_entity'):
            self.icon_entity = Entity(parent=self.model, name=f'button_icon_entity_{value}', model='quad', z=-.1, add_to_scene_entities=False)
        self.icon_entity.texture = value

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
            self.text_entity.world_scale = Vec3(value)


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
        if not self.text_entity.text or self.text_entity.text == '':
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
    from ursina import Ursina, application, Tooltip
    app = Ursina()
    b = Button(text='hello world!', color=color.azure, icon='sword', scale=.25, text_origin=(-.5,0))
    # b.fit_to_text()
    b.on_click = application.quit # assign a function to the button.
    b.tooltip = Tooltip('exit')

    app.run()
