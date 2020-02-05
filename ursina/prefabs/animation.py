from ursina import *


class Animation(Entity):

    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        temp_frame = Entity(
            model=name + '_' + str(0).zfill(6),
            texture=name + '_' + str(0).zfill(4),
            name='texture_search_frame',
            add_to_scene_entities=False,
            )

        found_texture = bool(temp_frame.texture)
        found_model = bool(temp_frame.model)
        # print('------------------', 'found_texture:', found_texture, 'found_model:', found_model, temp_frame.model)
        destroy(temp_frame)

        super().__init__()


        self.frames = list()

        if found_texture or found_model:
            for i in range(9999):
                frame = Entity(
                    parent=self,
                    name=str(i),
                    add_to_scene_entities=False,
                    )

                frame.model = 'quad' if not found_model else name + '_' + str(i).zfill(6)
                frame.texture = name + '_' + str(i).zfill(4)

                if found_texture and not frame.texture:
                    destroy(frame)
                    frame = self.frames[0]
                    break

                if found_model and not frame.model:
                    destroy(frame)
                    break

                for key, value in kwargs.items():
                    if key.startswith('origin') or key in ('double_sided', 'color'):
                        setattr(frame, key, value)
                    if key == 'filtering':
                        setattr(frame.texture, key, value)

                self.frames.append(frame)

        if found_texture:
            self.scale = (frame.texture.width/100, frame.texture.height/100)
            self.aspect_ratio = self.scale_x / self.scale_y

        self.stop()
        self.sequence = Sequence(loop=loop)

        for i in range(len(self.frames)):
            self.sequence.append(Func(self.stop))
            self.sequence.append(Func(setattr, self.frames[i], 'enabled', True))
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

    # texture_importer.textureless = True
    t = time.time()
    animation = Animation('ursina_wink', fps=2, scale=5, filtering=None)
    print(time.time()-t)
    # animation = Animation('blob_animation', fps=12, scale=5, y=20)
    #
    # from ursina.shaders import normals_shader
    # for f in animation.frames:
    #     f.shader = normals_shader
    #     f.set_shader_input('object_matrix', animation.getNetTransform().getMat())

    EditorCamera()
    app.run()
