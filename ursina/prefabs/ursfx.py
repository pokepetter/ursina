from ursina import *



# def play_synth_adsr(
#     wave = 'sine',
#     max_volume = .75,
#     # start_volume = 0,
#
#     attack = .05,
#     decay = .01,             # time to fade down to sustain volume
#     sustain_volume = .5,     # volume of middle part relative to max volume
#     sustain_length = .2,     # duration of middle part
#     release = .2,            # fade out duration
#     # release_volume = None,   # default is the same as sustain
#     # end_volume = 0,
#
#     start_pitch = 0,
#     end_pitch = 2,
#     pitch_curve = curve.linear,
#     # volume_multiplier = 1
#
#         ):
#
#     total_duration = attack + decay + sustain_length + release
#     # if release_volume is None:
#     #     release_volume = sustain_volume
#
#     a = Audio(wave, loop=True, pitch=pow(1 / 1.05946309436, -pitch), volume=start_volume)
#     a.animate('volume', max_volume, duration=attack, curve=curve.linear)
#     a.animate('volume', sustain_volume*max_volume, duration=decay, delay=attack, curve=curve.linear)
#     a.animate('volume', sustain_volume*max_volume, duration=sustain_length, delay=attack+decay, curve=curve.linear)
#     a.animate('volume', 0, duration=release, delay=attack+decay+sustain_length, curve=curve.linear)
#
#     a.animate('pitch', pow(1 / 1.05946309436, -end_pitch), duration=total_duration, curve=pitch_curve)
#     a.animations.append(invoke(a.stop, delay=total_duration))
#     return a


def ursfx(volume_curve, volume=.75, wave='sine', pitch=0, pitch_change=0, speed=1, pitch_curve=curve.linear):  # play a retro style sound effect
    a = Audio(wave, loop=True, pitch=pow(1 / 1.05946309436, -pitch), volume=volume_curve[0][1] * volume)

    cumulative_time = 0
    for i in range(len(volume_curve)-1):
        a.animate('volume', volume_curve[i+1][1] * volume, duration=(volume_curve[i+1][0] - volume_curve[i][0]) / speed, delay=volume_curve[i][0] / speed, curve=curve.linear)

    a.animate('pitch', pow(1 / 1.05946309436, -pitch-pitch_change), duration=volume_curve[i-1][0] / speed, curve=pitch_curve)
    a.animations.append(invoke(a.stop, delay=volume_curve[4][0] / speed))

    invoke(a.stop, delay=volume_curve[4][0] / speed)
    return a


class SynthGUI(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        default_positions = [(0,0), (.1,.9), (.15,.75), (.6,.75), (1,0)]
        self.wave_panel = Entity(parent=self, scale=.35, x=-0)
        self.waveform = Entity(parent=self.wave_panel, scale_y=.75)
        self.waveform_bg = Entity(parent=self.waveform, model='quad', origin=(-.5,-.5), z=.01, color=color.black66)
        # self.bg_2 = Entity(parent=self.waveform, model='quad', origin=(-.5,-.5), z=.01, color=color._16)
        self.volume_slider = Slider(parent=self.wave_panel, x=-.05, vertical=True, scale=1.95, min=.05, max=1, default=.75, step=.01, on_value_changed=self.play)

        self.wave_selector = ButtonGroup(('sine', 'triangle', 'square', 'noise'), parent=self.wave_panel, scale=.11, y=-.075)
        for e in self.wave_selector.buttons:
            e.text_entity.world_scale = .5

        self.pitch_slider = Slider(parent=self.wave_panel, y=-.25, scale=1.95, min=-36, max=36, default=0, step=1, on_value_changed=self.play, text='pitch')
        self.pitch_change_slider =  Slider(parent=self.wave_panel, y=-.325, scale=1.95, min=-12, max=12, default=0, step=1, on_value_changed=self.play, text='pitch change')
        self.speed_slider =  Slider(parent=self.wave_panel, scale=1.95, min=.5, max=4, default=1, step=.1, on_value_changed=self.play, y=-.4, text='speed')

        def coin_sound():
            self.paste_code(f"ursfx([(0,1), ({random.uniform(.05,.15)},.5), (.25,.5), ({random.uniform(.25,.5)},.5), (1,0)], pitch={random.randint(-3, 24)}, speed={random.uniform(2.5,3)})")
            self.play()

        self.coin_button = Button(text='coin', parent=self.wave_panel, scale=(.25, .125), origin=(-.5,.5), y=-.45, on_click=coin_sound)

        self.knobs = [Draggable(parent=self.waveform, scale=.05, model='circle', color=color.light_gray, highlight_color=color.azure, position=default_positions[i], i=i, min_y=0, max_y=1) for i in range(5)]
        self.knobs[0].lock = (True,False,True)

        self.line = Entity(parent=self.waveform, model=Mesh(vertices=[Vec3(0,0,0), Vec3(1,0,0)], mode='line', thickness=3), z=.01, color=color.light_gray)
        self.bg = Entity(parent=self.wave_panel, model='wireframe_quad', origin=(-.5,-.5), z=.02, color=color.black, scale_x=1)

        self.play_button = Button(text='>', parent=self.wave_panel, model='circle', scale=(.125, .125), color=color.azure, origin=(-.5,-.5), position=(-.075,1.025), on_click=self.play)
        self.copy_button = Button(text='copy', parent=self.wave_panel, scale=(.25, .125), color=color.dark_gray, origin=(-.5,-.5), position=(-.075+.125+.025, 1.025), on_click=self.copy_code)
        self.copy_button.text_entity.scale *= .5

        self.paste_button = Button(text='paste', parent=self.wave_panel, scale=(.25, .125), color=color.dark_gray, origin=(-.5,-.5), position=(self.copy_button.x + self.copy_button.scale_x + .025, 1.025), on_click=self.paste_code)
        self.paste_button.text_entity.scale *= .5

        self.code_text = Text('', parent=self.wave_panel, scale=2, position=(self.paste_button.x+self.paste_button.scale_x+.025,1.11))

        self.wave_selector.on_value_changed = self.play
        self.background_panel = Entity(model=Quad(radius=.025), parent=self.wave_panel, color=color.black66, z=1, origin=(-.5,-.5), scale=(1.125,1.75+.025), position=(-.1,-.6))

        for i, knob in enumerate(self.knobs):
            def drag(this_knob=knob):
                if this_knob.i == 0:
                    this_knob.min_x = 0
                else:
                    print(self.knobs[this_knob.i - 1].x)
                    this_knob.min_x = self.knobs[this_knob.i - 1].x + .01

                if this_knob.i == 4:
                    this_knob.max_x = 3
                else:
                    this_knob.max_x = self.knobs[this_knob.i + 1].x - .01

            knob.drag = drag

            def drop(this_knob=knob):
                self.play()
                self.bg.scale_x = self.knobs[4].x

                for e in self.knobs:
                    e.min_x = -0
                    e.max_x = 3

            knob.drop = drop

        self.draw()


    def update(self):
        for e in self.knobs:
            e.world_scale = .25
        if sum(int(e.dragging) for e in self.knobs) == 0:
            return

        self.draw()


    def input(self, key):
        if held_keys['control'] and key == 'v' and self.wave_panel.enabled:
            self.paste_code()


    def copy_code(self):
        print(self.recipe)
        import pyperclip
        pyperclip.copy(self.recipe)


    def paste_code(self, code=""):
        import pyperclip
        if not code:
            code = pyperclip.paste()

        print('paste code:', code)
        try:
            curve = code.split('ursfx(')[1].split(']')[0] + ']'
            curve = eval(curve)
            for i, e in enumerate(curve):
                self.knobs[i].position=(e)
            print('--------curve', curve)

            volume = .75
            if 'volume=' in code:
                volume = code.split('volume=')[1].split(',')[0]
                volume = eval(volume)
                self.volume_slider.value = volume
                print('--------volume', volume)

            wave = 'sine'
            if 'wave=' in code:
                wave = code.split('wave=')[1].split(',')[0]
                wave = eval(wave)
                self.wave_selector.value = wave
                print('--------wave', wave)

            pitch = 1
            if 'pitch=' in code:
                pitch = code.split('pitch=')[1]
                if ',' in pitch:
                    pitch = pitch.split(',')[0]
                else:
                    pitch = pitch[:-1]
                pitch = eval(pitch)
            self.pitch_slider.value = pitch
            print('--------pitch', pitch)


            pitch_change = 0
            if 'pitch_change=' in code:
                pitch_change = code.split('pitch_change=')[1]
                if ',' in pitch_change:
                    pitch_change = pitch_change.split(',')[0]
                else:
                    pitch_change = pitch_change[:-1]
                pitch_change = eval(pitch_change)
            self.pitch_change_slider.value = pitch_change
            print('--------pitch_change')

            speed = 1
            if 'speed=' in code:
                speed = code.split('speed=')[1]
                if ',' in speed:
                    speed = speed.split(',')[0]
                else:
                    speed = speed[:-1]
                speed = eval(speed)
            self.speed_slider.value = speed
            print('--------speed')


            print(curve, volume, wave, pitch, pitch_change, speed)
            self.draw()

        except:
            print('invalid ursfx code:', code)


    @property
    def recipe(self):
        pitch_code = ''
        if self.pitch_slider.value:
            pitch_code = f', pitch={self.pitch_slider.value}'

        pitch_change_code = ''
        if self.pitch_change_slider.value:
            pitch_change_code = f', pitch_change={self.pitch_change_slider.value}'

        speed_code = ''
        if speed_code != 1:
            speed_code = f', speed={round(self.speed_slider.value, 1)}'

        return f"ursfx({str(self.volume_curve)}, volume={round(self.volume_slider.value,3)}, wave='{self.wave_selector.value}'{pitch_code}{pitch_change_code}{speed_code})"






    def draw(self):
        # self.bg.scale_x = self.knobs[4].x
        self.waveform_bg.scale_x = self.knobs[4].x
        self.bg.scale_x = self.knobs[4].x

        for e in self.knobs:
            e.position = (round(e.x,2), round(e.y,2))


        self.line.model.vertices = [e.get_position(relative_to=self.waveform) for e in self.knobs]
        self.line.model.generate()

        self.volume_curve = [e.get_position(relative_to=self.waveform) for e in self.knobs]
        self.volume_curve = [(round(e[0],2), round(e[1],2)) for e in self.volume_curve]

        self.waveform.scale_y = self.volume_slider.value
        # self.code_text.text = f"ursfx({str(self.volume_curve)}, {round(self.volume_slider.value,3)}, wave='{self.wave_selector.value}', pitch={self.pitch_slider.value}, end_pitch={self.pitch_slider.value+self.pitch_change_slider.value})"


    def play(self):
        self.draw()
        # ursfx([(0.0, 0.0), (0.02, 0.89), (0.08, 0.63), (0.15, 0.27), (0.19, 0.0)], volume=0.75, wave='noise', pitch=-12, pitch_change=-9)
        # select = ursfx([(0.0, 0.0), (0.03, 0.9), (0.04, 0.75), (0.08, 0.25), (0.2, 0.0)], volume=0.75, wave='triangle', pitch=2, pitch_change=12)
        # select_2 = ursfx([(0.0, 0.0), (0.03, 0.9), (0.04, 0.75), (0.07, 0.18), (0.25, 0.0)], volume=0.86, wave='triangle', pitch=1, pitch_change=7)
        # hurt = ursfx([(0.0, 0.0), (0.03, 0.9), (0.04, 0.75), (0.06, 0.25), (0.22, 0.0)], volume=0.9, wave='noise', pitch=-12, pitch_change=-12)
        # heal = ursfx([(0.0, 0.0), (0.04, 0.9), (0.08, 0.04), (0.13, 0.66), (0.45, 0.0)], volume=1.0, wave='sine', pitch=-2, pitch_change=4)
        # coind = ursfx([(0.0, 1.0), (0.07, 0.5), (0.25, 0.5), (0.39, 0.5), (1.0, 0.0)], volume=0.75, wave='sine', pitch=24, speed=2.7)
        ursfx(
            [e.get_position(relative_to=self.waveform) for e in self.knobs],
            volume=self.volume_slider.value,
            wave=self.wave_selector.value,
            pitch=self.pitch_slider.value,
            pitch_change=self.pitch_slider.value + self.pitch_change_slider.value,
            speed=self.speed_slider.value
            )

        self.code_text.text = self.recipe

if __name__ == '__main__':
    app = Ursina()

gui = SynthGUI(enabled=False)

def toggle_gui_input(key):
    if key == 'f3':
        gui.enabled = not gui.enabled

Entity(input=toggle_gui_input)


if __name__ == '__main__':
    Sprite('shore', z=10, ppu=64, color=color.gray)
    gui.enabled = True
    app.run()
