from ursina import *

class Sky(Entity):
    instances = []

    def __init__(self, **kwargs):
        from ursina.shaders import unlit_shader
        super().__init__(parent=camera, name='sky', model='sky_dome', texture='sky_default', scale=9900, shader=unlit_shader, unlit=True)

        for key, value in kwargs.items():
            setattr(self, key, value)

        __class__.instances.append(self)


    def update(self):
        self.world_rotation = Vec3(0,0,0)
        self.scale = camera.clip_plane_far * .9

if __name__  == '__main__':
    app = Ursina()
    Sky(texture='sky_sunset')
    camera.fov = 90
    EditorCamera()

    # test
    def input(key):
        if key == '-':
            camera.clip_plane_far -= 100 +  (held_keys['control']*10)
            print(camera.clip_plane_far)
        elif key == '+':
            camera.clip_plane_far += 100 + (held_keys['control']*10)
            print(camera.clip_plane_far)

    app.run()
