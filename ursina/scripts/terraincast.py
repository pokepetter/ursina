from ursina import *


helper = None


def terraincast(world_position, terrain_entity, height_values=None, return_normals=False):    # uses x and z to return y on terrain.
    global helper
    if not helper:
        helper = Entity()

    helper.parent = terrain_entity.model
    helper.world_position = world_position

    pos = helper.get_position(relative_to=terrain_entity.model) + Vec3(.5,0,.5)

    if height_values is None:
        height_values = terrain_entity.model.height_values

    w, d = len(height_values), len(height_values[0])

    if pos.x >= 0 and pos.x < 1 and pos.z >= 0 and pos.z < 1:
        pos *= Vec3(w, 0, d)
        helper.y = height_values[int(pos.x)][int(pos.z)]
        x, _, z = pos

        point = height_values[int(floor(x))][int(floor(z))]
        normal = Vec3(0,0,0)

        if ceil(x) - x > 0 and ceil(z) - z > 0:
            point_e =  height_values[int(min(w-1, ceil(x)))][int(floor(z))]
            point_n =  height_values[int(floor(x))][int(min(d-1, ceil(z)))]
            point_ne = height_values[int(min(w-1, ceil(x)))][int(min(d-1, ceil(z)))]

            u0v0 = point * (ceil(x) - x) * (ceil(z) - z) # interpolated (x0, z0)
            u1v0 = point_e * (x - floor(x)) * (ceil(z) - z) # interpolated (x1, z0)
            u0v1 = point_n * (ceil(x) - x) * (z - floor(z)) # interpolated (x0, z1)
            u1v1 = point_ne * (x - floor(x)) * (z - floor(z)) # interpolated (x1, z1)

            point = u0v0 + u1v0 + u0v1 + u1v1  #estimate
            # normal = Vec3(2*(point_e-L), 2*(B-T), -4).Normalize();
            # print(point_e)
            if return_normals:
                normal = Vec3(0,1,0)
                p1 = Vec3(min(w-1, ceil(x)), point_e, floor(z))
                p2 = Vec3(floor(x), point, floor(z))
                p3 = Vec3(floor(x), point_n, min(d-1, ceil(z)))
                normal = (p2 - p1).cross(p3-p1).normalized()
                # print(normal)


        helper.y = point * terrain_entity.scale_y / 255
        if not return_normals:
            return helper.y

        return helper.y, normal

    if not return_normals:
        return None

    return None, None


if __name__ == '__main__':
    app = Ursina()

    terrain_entity = Entity(model=Terrain('heightmap_1', skip=8), scale=(40, 5, 20), texture='heightmap_1')
    player = Entity(model='sphere', color=color.azure, scale=.2, origin_y=-.5)


    hv = terrain_entity.model.height_values

    def update():
        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()
        player.position += direction * time.dt * 4

        player.y = terraincast(player.world_position, terrain_entity, hv)
        # test.world_position = player.world_position
        # test.look_at(test.world_position + normal)

    EditorCamera()
    Sky()

    app.run()
