from ursina import *

def uv_map(entity):

    norms = entity.model.generate_normals()
    tris = entity.model.triangles
    verts = entity.get_vertices(relative_to=scene)

    helper = Entity(model=Cone(3, direction=(0,0,1)), scale=.15, color=color.red)

    for t in tris[:1]:
        middle = (Vec3(verts[t[0]]) + Vec3(verts[t[1]]) + Vec3(verts[t[2]])) / 3
        helper.position = middle

        # direction = (Vec3(norms[t[0]]) + Vec3(norms[t[1]]) + Vec3(norms[t[2]])) / 3
        direction = Vec3(tuple(norms[t[0]])) + Vec3(tuple(norms[t[1]])) + Vec3(tuple(norms[t[2]])) / 3
        # direction =
        print(middle, direction)
        helper.look_at(middle+direction)


    # print(len(norms), len(tris))

    # for t in mesh.triangles:






if __name__ == '__main__':
    app = Ursina()

    # e = Entity(model='cube')
    e = Entity(model=Cylinder(), scale=4)
    uv_map(e)
    EditorCamera()
    app.run()
