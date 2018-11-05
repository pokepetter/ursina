from ursina import *
import os, shutil
import imageio


class VideoRecorder(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.recording = False
        self.file_path = os.path.join(application.asset_folder, 'video_temp')
        self.i = 0
        self.duration = 5
        self.frame_skip = 2

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

        if value:
            if os.path.exists(self.file_path):
                shutil.rmtree(self.file_path)   # delete temp folder
            os.makedirs(self.file_path)
            print('start recording, 5s', self.file_path)
            window.fps_counter = False
            window.exit_button.visible = False
            # base.movie(
            #     namePrefix = '\\video_temp\\test_recording',
            #     # namePrefix = '/video/test_recording',
            #  	duration = 3,
            #  	fps = 60,
            #  	format = 'png',
            #  	sd = 4,
            #  	# source = None
            #     )
            # invoke(self.convert_to_gif, delay=3.1)



        else:
            window.fps_counter = False
            window.exit_button.enabled = False

        self._recording = value

    def update(self):
        # self.duration += time.dt
        if self.i > 60/self.frame_skip * self.duration:
            if self.recording:
                self.convert_to_gif()
                self.recording = False

        if self.recording:
            # print(self.i)
            if self.i % self.frame_skip == 0:
                print(self.i / self.frame_skip)
                base.screenshot	(
                 	namePrefix = '\\video_temp\\test_recording' + '_' + str(self.i).zfill(4) + '.png',
                 	defaultFilename = 0,
                 	# source = None,
                 	# imageComment = ""
                    )
            self.i += 1


    def convert_to_gif(self):
        images = []
        if not os.path.exists(self.file_path):
            return

        for filename in os.listdir(self.file_path):
            # print(filename)
            images.append(imageio.imread(self.file_path + '/' + filename))

        imageio.mimsave(os.path.dirname(self.file_path)  + '/movie.gif', images)
        shutil.rmtree(self.file_path)   # delete temp folder
        print('saved gif to:', os.path.dirname(self.file_path)  + '/movie.gif')

# def screenshot	(
#  	namePrefix = 'screenshot',
#  	defaultFilename = 1,
#  	source = None,
#  	imageComment = ""
# )
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
