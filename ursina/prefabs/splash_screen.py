from ursina import *
from ursina.ursinamath import sample_gradient
from ursina.prefabs.particle_system import play_particle_system


class SplashScreen(Sprite):
    '''A simple splash screen that shows a static image'''

    def __init__(self, texture='ursina_logo', **kwargs):
        super().__init__(parent=camera.ui, texture=texture, world_z=camera.overlay.z-1, scale=.1, color=color.clear, **kwargs)

    def on_window_ready(self):
        camera.overlay.color = color.black
        self.animate_color(color.white, duration=2, delay=1, curve=curve.out_quint_boomerang)
        invoke(destroy, self, delay=3)


    def input(self, key):
        if key in ('space', 'gamepad a', 'escape', 'left mouse down'):
            destroy(self)


    def on_destroy(self):
        camera.overlay.animate_color(color.clear, duration=.25)


class UrsinaSplashScreen(Entity):
    def __init__(self):
        super().__init__(self, parent=camera.ui, world_z=camera.overlay.z-1, name='UrsinaSplashScreen')
        self.logo = Entity(parent=self, model='ursina_logo_wireframe', original_scale=.1, scale=.1, alpha=0)
        self.logo.model.colors = [hsv(lerp(240, 290, (v[0]+.5 + (v[1]*.25))), .8, .75) for v in self.logo.model.vertices]
        self.logo.model.generate()

        text = 'ursina engine'
        hues = (color.hex('#0c72d8'), color.hex('#a964df'), color.hex('#cc38a5'))
        colors = [sample_gradient(hues, i/len(text)) for i in range(len(text))]
        hsv_tags = [f'hsv({','.join([str(e) for e in colr.hsv])})' for colr in colors]

        text = ''.join([f'<{hsv_tags[i]}>{char}' for i, char in enumerate(text)])
        self.text_entity = Text(parent=self, text=text, origin=(0,0), y=-.175, original_scale=3.5, enabled=False)


    def on_destroy(self):
        camera.overlay.animate_color(color.clear, duration=.25)


    def input(self, key):
        if key in ('space', 'gamepad a', 'escape', 'left mouse down'):  # interrupt
            destroy(self)


    def on_window_ready(self):
        camera.overlay.color = color.black
        self.animations.append(invoke(self.play_animation, delay=.2))


    def play_animation(self):
        play_particle_system('ursina_splash_flourish', parent=self.logo, y=-1, scale=2)
        self.text_entity.enabled = False
        self.text_entity.scale = self.text_entity.original_scale
        self.logo.scale_y = 0
        self.logo.fade_in(duration=.05)
        self.logo.animate_scale_y(self.logo.original_scale, duration=3, curve=curve.out_elastic)

        @after(.2, entity=self, unscaled=False)
        def _show_text():
            self.text_entity.enabled = True
            self.text_entity.appear(.025)

        # from ursina.prefabs.ursfx import ursfx
        # from ursina.audio import pitch_note
        # ursfx([(0.0, 1.0), (0.12, 0.5), (0.25, 0.5), (0.46, 0.5), (1.0, 0.0)], volume=0.75, wave='sine', pitch=20, speed=2.7)
        # self.animations.append(invoke(ursfx, [(0.0, 0.0), (0.21, 0.54), (0.45, 0.76), (0.6, 0.75), (1.0, 0.0)], volume=0.53, wave='noise', pitch_change=-12, speed=2.0, delay=1))

        @after(1, entity=self, unscaled=False)
        def _close():
            self.logo.animate_rotation_y(-360, duration=.5, delay=.1, curve=curve.in_out_sine)
            self.logo.animate_scale_y(0, duration=.25, delay=.1, curve=curve.in_elastic)
            self.logo.fade_out(duration=.5)
            self.text_entity.animate_scale_y(0, delay=.4, duration=.2, curve=curve.in_back)
            self.text_entity.animate_scale_x(self.text_entity.original_scale*1.5, delay=.55, duration=.1, curve=curve.out_expo)
            invoke(self.on_destroy, delay=.65)



if __name__ == '__main__':
    app = Ursina(size=Vec2(1920,1080), )

    window.color = color.black
    ursina_splash_screen = UrsinaSplashScreen()

    # application.calculate_dt = False
    # time.dt =  1/60
    # from ursina.prefabs.video_recorder import VideoRecorder
    # vr = VideoRecorder(max_duration=3, fps=60, name='splash_screen')
    # def on_window_ready():
    #     vr.start_recording()


    # EditorCamera()



    # add a custom splash screen after the first one
    # ursina_splash.on_destroy = Func(SplashScreen, 'shore')
    app.run()
