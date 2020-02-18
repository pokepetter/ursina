from ursina import *

model_folders = ( # folder search order
    application.asset_folder,
    application.package_folder,
    )

texture_folders = ( # folder search order
    application.compressed_textures_folder,
    application.asset_folder,
    application.internal_textures_folder,
    )


class Animation(Entity):

    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        super().__init__()

        models = list()
        for folder in model_folders:
            models = list(folder.glob(f'**/{name}*.obj'))
            if models:
                break

        textures = list()
        for folder in texture_folders:
            textures = list(folder.glob(f'**/{name}*.png'))
            if textures:
                break

        self.frames = list()
        frame = None

        for i in range(max(len(models), len(textures))):
            model = 'quad'
            if i < len(models):
                model = models[i].stem

            frame = Entity(parent=self, model=model, add_to_scene_entities=False)

            if i < len(textures):
                frame.texture = textures[i].stem

                for key, value in kwargs.items():
                    if key.startswith('origin') or key in ('double_sided', 'color'):
                        setattr(frame, key, value)
                    if key == 'filtering':
                        setattr(frame.texture, key, value)

            self.frames.append(frame)

        if frame and frame.texture:
            self.scale = (frame.texture.width/100, frame.texture.height/100)
            self.aspect_ratio = self.scale_x / self.scale_y

        self.stop()
        self.sequence = Sequence(loop=loop)

        for frame in self.frames:
            self.sequence.append(Func(self.stop))
            self.sequence.append(Func(setattr, frame, 'enabled', True))
            self.sequence.append(Wait(1/fps))

        if autoplay:
            self.play()
        self.is_playing = autoplay

        for key, value in kwargs.items():
            setattr(self, key, value)


    def play(self):
        if self.is_playing:
            self.stop()
        self.sequence.start()
        self.is_playing = True


    def stop(self):
        for frame in self.frames:
            frame.enabled = False

        self.is_playing = False


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('color', 'origin'):
            for f in self.frames:
                setattr(f, name, value)

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e





if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    window.color = color.black

    animation = Animation('ursina_wink', fps=2, scale=5, filtering=None)
    # animation = Animation('blob_animation', fps=12, scale=5, y=20)
    #
    # from ursina.shaders import normals_shader
    # for f in animation.frames:
    #     f.shader = normals_shader
    #     f.set_shader_input('object_matrix', animation.getNetTransform().getMat())

    EditorCamera()
    app.run()
