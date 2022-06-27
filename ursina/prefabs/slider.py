from ursina import *


class Slider(Entity):
    def __init__(self, min=0, max=1, default=None, height=Text.size, text='', dynamic=False, radius=Text.size/2, bar_color=color.black66, **kwargs):
        super().__init__(add_to_scene_entities=False) # add later, when __init__ is done
        self.parent = camera.ui
        self.vertical = False
        self.min = min
        self.max = max

        if default is None:
            default = min
        self.default = default
        self.step = 0
        self.height = height

        self.on_value_changed = None    # set this to a function you want to be called when the slider changes
        self.setattr = None             # set this to (object, 'attrname') to set that value when the slider changes

        self.label = Text(parent=self, origin=(0.5, 0), x=-0.025, text=text)

        self.bg = Entity(parent=self, model=Quad(scale=(.525, height), radius=radius, segments=3),
            origin_x=-0.25, collider='box', color=bar_color)

        self.knob = Draggable(parent=self, min_x=0, max_x=.5, min_y=0, max_y=.5, step=self.step,
            model=Quad(radius=Text.size/2, scale=(Text.size, height)), collider='box', color=color.light_gray,
            text='0', text_origin=(0, -.55), z=-.1)

        def bg_click():
            self.knob.x = mouse.point[0]
            self.knob.start_dragging()
        self.bg.on_click = bg_click

        def drop():
            self.knob.z = -.1
            if self.setattr:
                if isinstance(self.setattr[0], dict):   # set value of dict
                    self.setattr[0][self.setattr[1]] = self.value
                else:                                   # set value of Entity
                    setattr(self.setattr[0], self.setattr[1], self.value)

            if self.on_value_changed:
                self.on_value_changed()


        self.knob.drop = drop
        self._prev_value = self.default
        self.value = self.default
        self.dynamic = dynamic    # if set to True, will call on_value_changed() while dragging. if set to False, will only call on_value_changed() after dragging.


        self.knob.text_entity.text = str(round(self.default, 2))

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.vertical:
            self.rotation_z = -90
            self.knob.lock = (1,0,0)
            self.knob.text_entity.rotation_z = 90
            self.knob.text_entity.position = (.015,0)
        else:
            self.knob.lock = (0,1,1)
            self.knob.text_entity.y = height/2

        scene.entities.append(self)


    @property
    def value(self):
        val = lerp(self.min, self.max, self.knob.x * 2)
        if isinstance(self.step, int) and not self.step == 0:
            val = int(round(val, 0))

        return val

    @value.setter
    def value(self, value):
        self.knob.x = (value - self.min) / (self.max - self.min) / 2
        self.slide()

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
        self.knob.step = value / (self.max-self.min) / 2

    def update(self):
        if self.knob.dragging:
            self.slide()

    def slide(self):
        t = self.knob.x / .5

        if self.step > 0:
            if isinstance(self.step, int) or self.step.is_integer():
                self.knob.text_entity.text = str(self.value)

        if self.dynamic and self._prev_value != t:
            if self.on_value_changed:
                self.on_value_changed()

            if self.setattr:
                target_object, attr = self.setattr
                setattr(target_object, attr, self.value)

            self._prev_value = t

        invoke(self._update_text, delay=1/60)

    def _update_text(self):
            self.knob.text_entity.text = str(round(self.value, 2))


    def __setattr__(self, name, value):
        if name == 'eternal':
            try:
                self.label.eternal = value
                self.bg.eternal = value
                self.knob.eternal = value
            except:
                pass
        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e



class ThinSlider(Slider):
    def __init__(self, *args, **kwargs):
        kwargs['height'] = Text.size
        super().__init__(*args, **kwargs)
        self.bg.model = Quad(scale=(.525, Text.size/5), radius=Text.size/10, segments=3)
        self.bg.origin = self.bg.origin
        self.bg.color = color.text_color
        self.bg.highlight_color = color.text_color
        self.knob.color = lerp(color.text_color, color.inverse(color.text_color), .1)
        self.label.color = color.text_color




if __name__ == '__main__':
    app = Ursina()

    box = Entity(model='cube', origin_y=-.5, scale=1, color=color.orange)

    def scale_box():
        box.scale_y = slider.value
        print(thin_slider.value)

    slider = Slider(0, 20, default=10, height=Text.size*3, y=-.4, step=1, on_value_changed=scale_box, vertical=True)

    thin_slider = ThinSlider(text='height', dynamic=True, on_value_changed=scale_box)

    thin_slider.label.origin = (0,0)
    thin_slider.label.position = (.25, -.1)

    app.run()
