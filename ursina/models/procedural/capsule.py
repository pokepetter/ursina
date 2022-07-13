from ursina import *


class Capsule(Mesh):
    def __init__(self, height=1, radius=.5, **kwargs):
        # make a capsule by stretching a sphere
        sphere_mesh = load_model('sphere', application.internal_models_compressed_folder)
        vertices = [Vec3(*v) + (Vec3(0,height,0) * int(v[1] > 0)) + Vec3(0,.5,0) for v in sphere_mesh.vertices]

        super().__init__(vertices=vertices, triangles=sphere_mesh.triangles, uvs=sphere_mesh.uvs, normals=sphere_mesh.normals, colors=sphere_mesh.colors, **kwargs)


if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Capsule(), texture='brick')
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
