from ursina import Button, Entity, Func, Mesh, Plane, ThinSlider, Vec2, Vec3, camera, color, copy, generate_properties_for_class, make_gradient
from ursina.prefabs.color_picker import ColorPicker

gradient_editor_arrow = Mesh(vertices=[(v+Vec3(0,-.4,0))*Vec3(.0175,.025,1) for v in (Vec3(0,0,0),Vec3(-.5,.5,0),Vec3(.5,.5,0),Vec3(-.5,.75,0),Vec3(.5,.75,0))], triangles=(0,2,1,1,2,4,4,3,1))

@generate_properties_for_class()
class GradientEditor(Entity):
    default_values = dict(parent=camera.ui, )

    def __init__(self, value={'0':color.hex('#ffffffff'), '32':color.hex('#ffffffff'),}, resolution=32, on_value_changed:callable=None, **kwargs):
        super().__init__(**(__class__.default_values | kwargs))

        self.color_picker = ColorPicker(parent=self, scale=.75, enabled=False, show_exit_button=True)
        self.color_picker.exit_button.on_click = self.stop_editing_color

        self.resolution = resolution
        self.sliders = []
        for i in range(3):
            slider = ThinSlider(parent=self, x=-.25, step=1, min=0, max=resolution-1, default=lerp(0,resolution,i/(3-1)), dynamic=True)
            self.sliders.append(slider)
            slider.knob.color=color.random_color()
            def _set_value():
                self.preview_gradient()
                if self.on_value_changed:
                    self.on_value_changed()

            slider.on_value_changed = _set_value
            slider.bg.enabled = False
            slider.knob.text_entity.enabled = False
            slider.knob.model = copy(gradient_editor_arrow)
            slider.knob.highlight_color = slider.knob.color
            slider.knob.on_double_click = Func(self.start_editing_color, slider)

        self.gradient_renderer = Entity(parent=self, model=Plane((resolution,1)), rotation_x=-90, scale=Vec3(.5,1,.05), y=-.035)
        self.copy_button = Button(parent=self, scale=Vec2(.05,.025)*1, text='copy', text_size=.5, origin=(.5,-.5), x=-.25-.01, y=-.06, on_click=self.copy)

        self.on_value_changed = on_value_changed    # set this to a function you want to be called when the slider changes
        self.value = value


    def start_editing_color(self, slider):
        if self.color_picker.enabled:
            self.stop_editing_color()

        self.color_picker.enabled = True
        self.color_picker.position = slider.knob.position + Vec2(-.25,.25*.75)
        self.color_picker.value = slider.knob.color

        def _set_color():
            slider.knob.color = self.color_picker.color
            self.value = self.value
        self.color_picker.on_value_changed = _set_color


    def stop_editing_color(self):
        self.color_picker.enabled = False
        self.color_picker.on_value_changed = None


    def preview_gradient(self):
        self.gradient_renderer.model.colors = [self.gradient[int((v.x+.5)*self.resolution)] for v in self.gradient_renderer.model.vertices]
        self.gradient_renderer.model.generate()

    def gradient_getter(self):  # get the final calculated gradient as a list of 32 color
        index_color_dict = self.value
        index_color_dict['0'] = min(self.sliders, key=lambda s:s.value).knob.color
        index_color_dict[str(self.resolution)] = max(self.sliders, key=lambda s:s.value).knob.color
        return make_gradient(index_color_dict)


    def value_getter(self):
        return {str(slider.value) : slider.knob.color for slider in self.sliders}

    def value_setter(self, value, call_on_value_changed=True):
        for i, (key, col) in enumerate(value.items()):
            if isinstance(col, str):
                col = color.hex(col)

            self.sliders[i].knob.color = col
            self.sliders[i].value_setter(int(key), call_on_value_changed=False)

        self._value = value
        self.preview_gradient()
        if self.on_value_changed and call_on_value_changed:
            self.on_value_changed()

    def copy(self):
        # print('copied:', {key:color.rgb_to_hex(*col) for key, col in self.value.items()})
        import pyperclip
        pyperclip.copy(str({key:color.rgb_to_hex(*col) for key, col in self.value.items()}))


if __name__ == '__main__':
    from ursina import Ursina
    app = Ursina()
    GradientEditor()
    app.run()