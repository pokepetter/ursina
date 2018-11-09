from ursina import *
import os, shutil
import imageio


class VideoRecorder(Entity):
    def __init__(self, duration=5, name='untitled_video', **kwargs):
        super().__init__()
        self.recording = False
        self.file_path = Path(application.asset_folder) / 'video_temp'
        self.i = 0
        self.duration = duration
        self.frame_skip = 2     # 30 fps
        self.video_name = name

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == 'f10':
            self.recording = not self.recording
        if key == 'f':
            self.convert_to_gif()

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
            window.fps_counter = False
            window.exit_button.visible = False
        else:
            window.fps_counter = False
            window.exit_button.enabled = False

        self._recording = value

    def update(self):
        if self.i > 60/self.frame_skip * self.duration:
            if self.recording:
                self.convert_to_gif()
                self.recording = False

        if self.recording:
            if self.i % self.frame_skip == 0:
                print(self.i / self.frame_skip)
                base.screenshot	(
                 	namePrefix = '\\video_temp\\' + self.video_name + '_' + str(self.i).zfill(4) + '.png',
                 	defaultFilename = 0,
                    )
            self.i += 1


    def convert_to_gif(self):
        images = []
        if not os.path.exists(self.file_path):
            return

        for filename in os.listdir(self.file_path):
            # print(filename)
            images.append(imageio.imread(self.file_path/filename))

        imageio.mimsave(Path(f'{self.file_path.parent}/{self.video_name}.gif'), images)
        shutil.rmtree(self.file_path)   # delete temp folder
        print('saved gif to:', Path(f'{self.file_path.parent}/{self.video_name}.gif'))



if __name__ == '__main__':
    app = Ursina()
    window.size = (1600/3,900/3)
    cube = primitives.RedCube()
    cube.animate_x(5, duration=5, curve='linear')
    vr = VideoRecorder()
    invoke(setattr, vr, 'recording', True, delay=1)
    # invoke(os._exit, 0, delay=6)
    # vr.recording = True
    app.run()
