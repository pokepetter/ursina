from copy import deepcopy

from ursina import *


class Quad(Mesh):
    _cache = {}
    _corner_maker = None
    _point_placer = None

    def __new__(cls, radius=.1, segments=8, aspect=1, scale=(1,1), mode='ngon', thickness=1):
        # special case: plain quad
        if radius == 0 and aspect == 1 and scale == (1, 1) and mode == 'ngon':
            return Mesh(
                vertices=[
                    Vec3(-0.5, -0.5, 0.0), Vec3(0.5, -0.5, 0.0),
                    Vec3(0.5, 0.5, 0.0), Vec3(-0.5, 0.5, 0.0)
                ],
                triangles=[(0, 1, 2, 3)],
                uvs=[Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)],
                mode='triangle'
            )

        key = (radius, segments, aspect, scale, mode, thickness)
        if key in cls._cache:
            try:
                return deepcopy(cls._cache[key])
            except:     # deepcopy can fail if the model has been destroyed
                pass
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance

    def __init__(self, radius=.1, segments=8, aspect=1, scale=(1,1), mode='ngon', thickness=1):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        if not Quad._corner_maker:
            Quad._corner_maker = Entity(eternal=True, add_to_scene_entities=False)
        if not Quad._point_placer:
            Quad._point_placer = Entity(parent=Quad._corner_maker, x=-radius, eternal=True, add_to_scene_entities=False)

        super().__init__()
        self.radius = radius
        self.mode = mode
        self.thickness = thickness

        self.vertices = [Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(1, 1, 0), Vec3(0, 1, 0)]

        _segments = segments + 1
        if _segments > 1:
            new_verts = []
            Quad._corner_maker.rotation_z = -90 / _segments / 2
            Quad._corner_maker.position = Vec3(0, 0, 0)
            Quad._point_placer.position = Vec3(-radius, 0, 0)

            corrections = [Vec3(radius, radius, 0), Vec3(-radius, radius, 0),
                           Vec3(-radius, -radius, 0), Vec3(radius, -radius, 0)]

            for j in range(4):
                Quad._corner_maker.position = self.vertices[j] + corrections[j]
                for i in range(_segments):
                    new_verts.append(Quad._point_placer.world_position)
                    Quad._corner_maker.rotation_z -= 90 / _segments

            self.vertices = new_verts

        self.uvs = [Vec2(v[0], v[1]) for v in self.vertices]

        # aspect correction
        for v in self.vertices:
            if v[0] < .5:
                v[0] /= aspect
            else:
                v[0] = lerp(v[0], 1, 1 - (1 / aspect))

        # scale correction
        for v in self.vertices:
            if v[0] > .5:
                v[0] += (scale[0] - 1)
            if v[1] > .5:
                v[1] += (scale[1] - 1)

        # center mesh
        offset = sum(self.vertices) / len(self.vertices)
        self.vertices = [(v[0] - offset[0], v[1] - offset[1], v[2] - offset[2]) for v in self.vertices]

        if mode == 'line':
            self.vertices.append(self.vertices[0])

        self.normals = [Vec3.back for _ in self.vertices]
        self.generate()


if __name__ == '__main__':
    app = Ursina()
    from time import perf_counter
    t = perf_counter()
    # m =
    for i in range(100):
        Entity(model=Quad(scale=(3,1), thickness=3, segments=3, mode='line'), color = color.hsv(0,1,1,.7))
    # Entity(scale=(3,1), model=Quad(aspect=3), color = color.hsv(60,1,1,.3))
    print('-------', (perf_counter() - t))

    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    # ed = EditorCamera(rotation_speed = 200, panning_speed=200)

    Entity(model=Quad(0), texture='shore', x=-1)

    camera.z = -5
    app.run()
