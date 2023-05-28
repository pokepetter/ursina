from ursina.prefabs.button import Button
from ursina.entity import Entity
from ursina.vec2 import Vec2
from ursina.prefabs.input_field import InputField, ContentTypes
from ursina import color, camera


class VecField(Button):
    def __init__(self, default_value=Vec2(0,0), character_limit=12, **kwargs):
        kwargs = dict(parent=camera.ui, scale=(.5,.05), default_value=default_value, character_limit=character_limit, text='', text_origin=(-.5,0), color=color.black90) | kwargs
        super().__init__(**kwargs)
        self.fields = []
        self.on_value_changed = None
        w = 1 / len(default_value) *.5

        self.highlight_color = self.color
        self.pressed_color = self.color

        for i in range(len(default_value)):
            field = InputField(str(self.default_value[i])[:self.character_limit], character_limit=self.character_limit, model='quad', parent=self, limit_content_to=ContentTypes.math,
                x=(i*w)+w/2, scale=(w,1), z=-1, color=color._8, font='VeraMono.ttf', submit_on=['enter','tab'])
            field.grid = Entity(parent=field, model='wireframe_quad', color=color.dark_gray)
            field.text_field.scale *= .75
            field.on_submit = self.convert_text_to_vector
            field.on_value_changed = self.convert_text_to_vector
            self.fields.append(field)

        self.value = default_value


    def convert_text_to_vector(self):
        vector = []
        for i, field in enumerate(self.fields):
            try:
                # value = type(self.default_value[i])(eval(field.text[:self.character_limit]))
                value = float(eval(field.text[:self.character_limit]))
                if isinstance(value, float):
                    vector.append(value)
                    field.text_field.text_entity.text = str(value)[:8]
            except: # invalid/incomplete math
                print('invalid')
                return
        print('-------------', self.default_value, type(self.default_value))
        # print('vector:', vector, 'fotype', type(self.default_value))
        if not isinstance(self.default_value, (tuple, list)):
            vector = type(self.default_value)(*vector)

        self.value = vector


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # for i, field in enumerate(self.fields):
        #     field.text_field.text_entity.text = str(value[i])[:self.character_limit]

        self._value = value
        if self.on_value_changed is not None:
            self.on_value_changed()




if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(parent=camera.ui, model='quad', scale=.05, z=-10)
    field = VecField(text=' field', default_value=Vec3(0,0,0))
    def on_value_changed():
        print('set value to:', field.value)

    field = VecField(default_value=[10,1], y=-.2)
    # field.on_value_changed = on_value_changed

    Entity(color=color.azure, scale=(.5,.05), model='quad', parent=camera.ui)
    InputField(y=-.1)

    app.run()
