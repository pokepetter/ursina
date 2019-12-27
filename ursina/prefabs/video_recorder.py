from ursina import *
import os, shutil
# import imageio    # gets imported in convert_to_gif


class VideoRecorder(Entity):
    def __init__(self, duration=5, name='untitled_video', **kwargs):
        super().__init__()
        self.recording = False
        self.file_path = Path(application.asset_folder) / 'video_temp'
        self.i = 0
        self.duration = duration
        self.frame_skip = 2  # 30 fps
        self.video_name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key):
        if key == 'f10':
            self.recording = not self.recording


    @property
    def recording(self):
        return self._recording

    @recording.setter
    def recording(self, value):

        if value == True:
            if self.file_path.exists():
                shutil.rmtree(self.file_path)   # delete temp folder
            self.file_path.mkdir()
            print('start recording,', self.duration, self.file_path)
            window.fps_counter.enabled = False
            window.exit_button.visible = False
        else:
            window.fps_counter.enabled = True
            window.exit_button.visible = True

        self._recording = value

    def update(self):
        if self.i > 60/self.frame_skip * self.duration:
            if self.recording:
                self.convert_to_gif()
                self.recording = False

        if self.recording:
            if self.i % self.frame_skip == 0:
                print(self.i / self.frame_skip)
                base.screenshot(
                 	namePrefix = '\\video_temp\\' + self.video_name + '_' + str(self.i).zfill(4) + '.png',
                 	defaultFilename = 0,
                    )
            self.i += 1

    # store screenshot in memory
    def renderToPNM(self):
        # Render the frame
        base.graphicsEngine.renderFrame()

        ### FETCHING THE RENDERED IMAGE
        image = PNMImage()
        # Set display region to the default
        dr = base.camNode.getDisplayRegion(0)
        # Store the rendered frame into the variable screenshot
        dr.getScreenshot(image)

        return image

    def convert_to_gif(self):
        import imageio
        images = []
        if not os.path.exists(self.file_path):
            return

        for filename in os.listdir(self.file_path):
            # print(filename)
            images.append(imageio.imread(self.file_path/filename))

        imageio.mimsave(Path(f'{self.file_path.parent}/{self.video_name}.gif'), images)
        shutil.rmtree(self.file_path)   # delete temp folder
        print('saved gif to:', Path(f'{self.file_path.parent}/{self.video_name}.gif'))



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
        application.video_recorder.duration = float(self.duration_field.text)
        application.video_recorder.video_name = self.name_field.text
        application.video_recorder.frame_skip = 60 // int(self.fps_field.text)
        application.video_recorder.recording = True




if __name__ == '__main__':
    app = Ursina()
    # window.size = (1600/3,900/3)
    cube = primitives.RedCube()
    cube.animate_x(5, duration=5, curve=curve.linear)
    cube.animate_x(0, duration=5, curve=curve.linear, delay=5)
    # vr = VideoRecorder()
    # invoke(setattr, vr, 'recording', True, delay=1)
    # invoke(os._exit, 0, delay=6)
    # vr.recording = True
    Cursor()
    app.run()
