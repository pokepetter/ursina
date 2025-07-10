
from math import ceil, floor

from ursina.array_tools import Array2D, chunk_list, enumerate_2d
from ursina.ursinamath import clamp


def chunk_mesh(mesh, num_chunks, chunk_size=1/8):
    if not hasattr(mesh, 'vertices'):
        raise Exception(f'{mesh} has no vertices')

    chunks = Array2D(width=num_chunks[0], height=num_chunks[1])
    for (x,z), _value in enumerate_2d(chunks):
        chunks[x][z] = []

    polys = list(chunk_list(mesh.generated_vertices, 3))

    for i, tri in enumerate(polys):
        if chunk_size >= 1:
            min_x = floor(min(v.x for v in tri) / chunk_size)
            min_y = floor(min(v.z for v in tri) / chunk_size)
            max_x = ceil(max(v.x for v in tri) / chunk_size)
            max_y = ceil(max(v.z for v in tri) / chunk_size)
        else:
            min_x = floor(min(v.x for v in tri) / chunk_size)
            min_y = floor(min(v.z for v in tri) / chunk_size)
            max_x = ceil(max(v.x for v in tri) / chunk_size)
            max_y = ceil(max(v.z for v in tri) / chunk_size)

        min_x = clamp(min_x, 0, chunks.width-1)
        max_x = clamp(max_x, 0, chunks.width-1)
        min_y = clamp(min_y, 0, chunks.height-1)
        max_y = clamp(max_y, 0, chunks.height-1)

        # print(min_x, max_x, min_y, max_y)
        for x in range(min_x, max_x+1):
            for y in range(min_y, max_y+1):
                # print('append tri', i, 'to chunk', x, y)
                chunks[x][y].append(tri)

    return chunks

if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Grid, Mesh, Terrain, Ursina, Vec2, Vec3, color, flatten_list
    app = Ursina()

    reference = Entity(x=-1, model=Terrain('heightmap_1', skip=4), texture='grass', texture_scale=(3,3), origin=(-.5,0,-.5), wireframe=True, color=color.green)
    target_mesh = reference.model
    target_mesh.vertices = [v+Vec3(.5,0,.5) for v in target_mesh.vertices]
    chunk_size = 1/8
    num_chunks = Vec2(8,8)
    chunks = chunk_mesh(target_mesh, num_chunks, chunk_size)
    grid = Entity(x=-1, model=Grid(*num_chunks), rotation_x=90, color=color.red, scale=num_chunks*chunk_size, origin=(-.5,-.5))

    for (x,z), value in enumerate_2d(chunks):
        if not value:
            chunks[x][z] = Entity(model='cube', color=color.random_color(), position=Vec3(x-1,0,z)*chunk_size, origin=(-.5,-.5,-.5), scale=chunk_size)
            continue
        chunks[x][z] = Entity(x=-1, model=Mesh(vertices=flatten_list(value)), color=color.random_color())


    # target_mesh = load_model('tower_collider.ursinamesh')
    # reference = Entity(model=target_mesh, wireframe=True)
    # chunk_size = 8
    # num_chunks = Vec2(5,7)
    # chunks = chunk_mesh(target_mesh, num_chunks, chunk_size)
    # grid = Entity(model=Grid(*num_chunks), rotation_x=90, color=color.red, scale=num_chunks*chunk_size, origin=(-.5,-.5))

    # for (x,z), value in enumerate_2d(chunks):
    #     if not value:
    #         chunks[x][z] = Entity(model='wireframe_cube', color=color.random_color(), position=Vec3(x,0,z)*chunk_size, origin=(-.5,-.5,-.5), scale=chunk_size)
    #         continue
    #     chunks[x][z] = Entity(model=Mesh(vertices=flatten_list(value)), color=color.random_color())

    EditorCamera()

    app.run()