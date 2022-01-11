from ursina import *

cached_quads = {}
def Quad(radius=.1, segments=8, aspect=1, scale=(1,1), mode='ngon', thickness=1):

    if radius == 0 and aspect==1 and scale == (1,1) and mode == 'ngon':
        return Mesh(
            vertices=[Vec3(-0.5, -0.5, 0.0), Vec3(0.5, -0.5, 0.0), Vec3(0.5, 0.5, 0.0), Vec3(-0.5, 0.5, 0.0)],
            triangles=[(0,1,2,3), ],
            uvs=[Vec2(0,0), Vec2(1,0), Vec2(1,1), Vec2(0,1)],
            mode='triangle'
            )
    # copy a cached quad if a QuadMesh with the same settings have been created before
    quad_identifier = f'QuadMesh({radius}, {segments}, {aspect}, {scale}, {mode}, {thickness})'
    if quad_identifier in cached_quads and cached_quads[quad_identifier]:
        # print('load cached')
        return deepcopy(cached_quads[quad_identifier])

    return QuadMesh(radius, segments, aspect, scale, mode, thickness)


class QuadMesh(Mesh):
    corner_maker = None
    point_placer = None

    def __init__(self, radius=.1, segments=8, aspect=1, scale=(1,1), mode='ngon', thickness=1):
        if not QuadMesh.corner_maker: QuadMesh.corner_maker = Entity(eternal=True, add_to_scene_entities=False)
        if not QuadMesh.point_placer: QuadMesh.point_placer = Entity(parent=QuadMesh.corner_maker, x=-radius, eternal=True, add_to_scene_entities=False)


        super().__init__()
        self.vertices = [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0)]
        self.radius = radius
        self.mode = mode
        self.thickness = thickness

        _segments = segments
        _segments += 1
        if _segments > 1:
            new_verts = list()
            QuadMesh.corner_maker.rotation_z = 0
            QuadMesh.corner_maker.position = Vec3(0,0,0)
            QuadMesh.corner_maker.rotation_z -= 90/_segments/2
            QuadMesh.point_placer.position = Vec3(-radius,0,0)

            corner_corrections = (Vec3(radius,radius,0), Vec3(-radius,radius,0), Vec3(-radius,-radius,0), Vec3(radius,-radius,0))
            for j in range(4):  # 4 corners
                QuadMesh.corner_maker.position = self.vertices[j] + corner_corrections[j]
                for i in range(_segments):
                    new_verts.append(QuadMesh.point_placer.world_position)
                    QuadMesh.corner_maker.rotation_z -= 90/_segments

            self.vertices = new_verts


        self.uvs = list()
        for v in self.vertices:
            self.uvs.append((v[0], v[1]))

        # scale corners horizontally with aspect
        for v in self.vertices:
            if v[0] < .5:
                v[0] /= aspect
            else:
                v[0] = lerp(v[0], 1, 1-(1/aspect))

        # move edges out to keep nice corners
        for v in self.vertices:
            if v[0] > .5:
                v[0] += (scale[0]-1)
            if v[1] > .5:
                v[1] += (scale[1]-1)


        # center mesh
        offset = sum(self.vertices) / len(self.vertices)
        self.vertices = [(v[0]-offset[0], v[1]-offset[1], v[2]-offset[2]) for v in self.vertices]


        # make the line connect back to start
        if mode == 'line':
            self.vertices.append(self.vertices[0])

        self.generate()
        cached_quads[f'QuadMesh({radius}, {segments}, {aspect}, {scale}, {mode}, {thickness})'] = self




if __name__ == '__main__':
    app = Ursina()
    from time import perf_counter
    t = perf_counter()
    # m =
    for i in range(100):
        Entity(model=Quad(scale=(3,1), thickness=3, segments=3, mode='line'), color = color.color(0,1,1,.7))
    # Entity(scale=(3,1), model=Quad(aspect=3), color = color.color(60,1,1,.3))
    print('-------', (perf_counter() - t))

    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    # ed = EditorCamera(rotation_speed = 200, panning_speed=200)

    Entity(model=Quad(0), texture='shore', x=-1)

    camera.z = -5
    app.run()
