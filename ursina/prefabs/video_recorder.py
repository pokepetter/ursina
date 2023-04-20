from ursina import *
import os, shutil
import numpy as np


class VideoRecorder(Entity):
    def __init__(self, max_duration=5, name='untitled_video', **kwargs):
        super().__init__()
        self.recording = False
        self.file_path = Path(application.asset_folder) / 'video_temp'
        self.i = 0
        self.max_duration = max_duration
        self.fps = 30
        self.video_name = name
        self.t = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.max_frames = int(self.max_duration * self.fps)
        self.frames = []


    def start_recording(self):
        print('start recording,', self.max_duration, self.file_path)
        window.fps_counter.enabled = False
        window.exit_button.visible = False
        self.frames = []
        self.max_frames = self.max_duration * self.fps

        if self.file_path.exists():
            shutil.rmtree(self.file_path)   # delete temp folder

        if not self.file_path.exists():
            self.file_path.mkdir()
        # base.movie(namePrefix=f'\\video_temp\\{self.video_name}', max_duration=2.0, fps=30, format='mp4', sd=4)

        application.calculate_dt = True
        time.dt = 1/self.fps
        self.recording = True
        invoke(self.stop_recording, delay=self.max_duration)



    def stop_recording(self):
        self.recording = False
        window.fps_counter.enabled = True
        window.exit_button.visible = True
        print('stop recording')
        # self.convert_to_gif()
        # command = 'ffmpeg -framerate 60 -f image2 -i video_temp/%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p untitled_video.webm'
        command = f'ffmpeg -framerate 60 -f image2 -i {self.file_path}/untitled_video_%04d.png {self.video_name}.mp4'
        result = subprocess.Popen(command, shell=True)
        application.calculate_dt = True

        # print('converting to video:', result)
        print('saved webm to:', Path(f'{self.file_path.parent}/{self.video_name}.webm'))

    def update(self):
        if not self.recording:
            return

        time.dt = 1/60
        base.screenshot(namePrefix=self.file_path / f'{self.video_name}_{str(self.i).zfill(4)}.png', defaultFilename=0)
        self.i += 1

    def input(self, key):
        combo = ['control', 'r', 'e', 'c']
        if key in combo and all([held_keys[e] for e in combo]):
            if not self.recording:
                self.start_recording()
            else:
                self.stop_recording()


class VideoRecorderUI(WindowPanel):
    def __init__(self, **kwargs):
        self.duration_label = Text('duration:')
        self.duration_field = InputField(default_value='5')
        self.fps_label = Text('fps:')
        self.fps_field = InputField(default_value='30')
        self.name_label = Text('name:')
        self.name_field = InputField(default_value='untitled_video')

        self.start_button = Button(text='Start Recording [Shift+F12]', color=color.azure, on_click=self.start_recording)

        super().__init__(
            title='Video Recorder [F12]',
            content=(
                self.duration_label,
                self.duration_field,
                self.fps_label,
                self.fps_field,
                self.name_label,
                self.name_field,
                Space(1),
                self.start_button,
                ),
            )
        self.y = .5
        self.scale *= .75
        self.visible = False


    def input(self, key):
        if key == 'f12':
            self.visible = not self.visible

        if held_keys['shift'] and key == 'f12':
            self.start_button.on_click()


    def start_recording(self):
        print(self.name_field)
        if self.name_field.text == '':
            self.name_field.blink(color.color(0,1,1,.5), .5)
            print('enter name')
            return

        # self.start_button.color=color.lime
        self.visible = False
        application.video_recorder.max_duration = float(self.max_duration.text)
        application.video_recorder.video_name = self.name_field.text
        application.video_recorder.frame_skip = 60 // int(self.fps_field.text)
        application.video_recorder.recording = True



if __name__ == '__main__':
    app = Ursina()
    window.size = (1280*.5, 720*.5)
    from ursina.prefabs.first_person_controller import FirstPersonController
    from ursina.shaders import lit_with_shadows_shader
    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))

    editor_camera = EditorCamera(enabled=False, ignore_paused=True)
    player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8)
    player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

    gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=False)

    shootables_parent = Entity()
    mouse.traverse_target = shootables_parent

    for i in range(16):
        Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
            x=random.uniform(-8,8),
            z=random.uniform(-8,8) + 8,
            collider='box',
            scale_y = random.uniform(2,3),
            color=color.hsv(0, 0, random.uniform(.9, 1))
            )


    sun = DirectionalLight()
    sun.look_at(Vec3(1,-1,-1))
    Sky()

    vr = VideoRecorder(max_duration=120)



    app.run()
