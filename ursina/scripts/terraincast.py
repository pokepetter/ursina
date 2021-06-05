from ursina import *
from ursina import distance as ursina_distance
from math import inf
from ursina.hit_info import HitInfo



def prepare_terrain(terrain, debug=False, calculate_normals=True):

    #does calculations that are needed for every terraincast check, and sets up the entities that manage transofrmations
    #has the option to calculate all face normals for the terrain (quicker while running, but takes time to initiate)

    terrain._cast = Entity(parent=terrain,
                           model='sphere',
                           color=color.orange,
                           world_scale=0.1,
                           position=(0, 1, 0),
                           visible=debug,)
    if debug:
        terrain._cast.bound = Entity(parent=terrain,
                                     model='cube',
                                     color=color.rgba(255, 0, 0, 100))

    terrain._cast.direction = Entity(parent=terrain,
                                     position=(0, 1, 0))

    height_values = terrain.model.height_values

    terrain._cast.width = terrain.model.width
    terrain._cast.depth = terrain.model.depth
    terrain._cast.aspect_ratio = terrain._cast.depth / terrain._cast.width

    #correction_scale needed to account for cases where the other dimension is the smaller, so treated as 1 now
    if terrain._cast.depth < terrain._cast.width:
        terrain._cast.correction_scale = 1 / terrain._cast.aspect_ratio
    else:
        terrain._cast.correction_scale = 1

    terrain._cast.max = max([max(i) for i in height_values])
    terrain._cast.min = min([min(i) for i in height_values])

    if calculate_normals:
        terrain._cast.prepared_height_values = []
        for scan_x, v in enumerate(height_values):
            row_to_add = []
            for scan_z, w in enumerate(v):
                quad_to_add = []
                for sub_face in [False, True]:
                    quad_to_add.append(_terraincast_get_plane(terrain, scan_x, scan_z, sub_face))
                row_to_add.append(quad_to_add)
            terrain._cast.prepared_height_values.append(row_to_add)


def _terraincast_get_plane(terrain, scan_x, scan_z, sub_face):
    #gets details needed for each plane that makes up the terrain
    from numpy import cross
    height_values = terrain.model.height_values
    if scan_z == len(height_values[0]) - 1 and scan_x == len(height_values) - 1:
        start = Vec3(scan_x, height_values[scan_x][scan_z], scan_z)
        right = Vec3(scan_x + 1, height_values[scan_x][scan_z], scan_z)
        left = Vec3(scan_x, height_values[scan_x][scan_z], scan_z + 1)

    elif scan_z == len(height_values[0]) - 1:
        start = Vec3(scan_x, height_values[scan_x][scan_z], scan_z)
        right = Vec3(scan_x, height_values[scan_x][scan_z], scan_z + 1)
        left = Vec3(scan_x + 1, height_values[scan_x + 1][scan_z], scan_z + 1)
        # print('edge')

    elif scan_x == len(height_values) - 1:
        start = Vec3(scan_x, height_values[scan_x][scan_z], scan_z)
        right = Vec3(scan_x, height_values[scan_x][scan_z + 1], scan_z + 1)
        left = Vec3(scan_x + 1, height_values[scan_x][scan_z + 1], scan_z + 1)

    elif sub_face:
        start = Vec3(scan_x, height_values[scan_x][scan_z], scan_z)
        right = Vec3(scan_x, height_values[scan_x][scan_z + 1], scan_z + 1)
        left = Vec3(scan_x + 1, height_values[scan_x + 1][scan_z + 1], scan_z + 1)

    else:
        start = Vec3(scan_x, height_values[scan_x][scan_z], scan_z)
        right = Vec3(scan_x + 1, height_values[scan_x + 1][scan_z], scan_z)
        left = Vec3(scan_x + 1, height_values[scan_x + 1][scan_z + 1], scan_z + 1)

    normal = cross(left - start, right - start)
    if normal[1] < 0:
        normal = - normal
    normal = normal.tolist()
    normal = Vec3(*normal).normalized()

    return start, normal


def terraincast(origin,
                terrain,
                direction=Vec3(0, -1, 0),
                distance=inf,
                iterations=inf,
                debug=False,
                calculate_normals=True,
                ):
    from numpy import dot
    origin = Vec3(*origin)
    direction = Vec3(*direction)

    height_values = terrain.model.height_values
    current_iterations = 0

    if not hasattr(terrain, "_cast"):
        prepare_terrain(terrain, debug, calculate_normals)

    #transformations to make terraincast line up with model space, then "height_values grid" space
    terrain._cast.world_position = origin
    terrain._cast.position += terrain.origin

    terrain._cast.direction.world_position = terrain.world_position + direction.normalized()

    model_origin = terrain._cast.position
    model_origin[0] = model_origin[0] / terrain._cast.correction_scale
    model_origin[2] = model_origin[2] / terrain._cast.correction_scale

    model_origin = model_origin + Vec3(0.5, 0, 0.5 * terrain._cast.aspect_ratio)

    model_direction = terrain._cast.direction.position
    model_direction[1] = model_direction[1] * terrain._cast.correction_scale

    #sets up scan information that iterates through the grid (height_values "grid" space essentially)
    scan_direction = Vec3(model_direction[0] * terrain._cast.width, model_direction[1],
                          model_direction[2] * terrain._cast.width)
    scan_tile = Vec3(model_origin[0] * terrain._cast.width, model_origin[1], model_origin[2] * terrain._cast.width)
    original_tile = Vec3(model_origin[0] * terrain._cast.width, model_origin[1], model_origin[2] * terrain._cast.width)

    scan_max_distance = ursina_distance(Vec3(0, 0, 0), scan_direction) * distance

    searching = True
    sub_face = False

    # handle case where ray starts outside model
    x_scalar = 0
    y_scalar = 0
    z_scalar = 0

    if scan_tile[0] < 0 and scan_direction[0] > 0:
        x_scalar = (0 - scan_tile[0]) / scan_direction[0]
    elif scan_tile[0] > len(height_values) and scan_direction[0] < 0:
        x_scalar = abs((scan_tile[0] - (len(height_values))) / scan_direction[0])

    if scan_tile[2] < 0 and scan_direction[2] > 0:
        z_scalar = (0 - scan_tile[2]) / scan_direction[2]
    elif scan_tile[2] > len(height_values[0]) and scan_direction[2] < 0:
        z_scalar = abs((scan_tile[2] - (len(height_values[0]))) / scan_direction[2])

    if scan_tile[1] < terrain._cast.min and scan_direction[1] > 0:
        y_scalar = (terrain._cast.min - scan_tile[1]) / scan_direction[1]
    elif scan_tile[1] > terrain._cast.max and scan_direction[1] < 0:
        y_scalar = abs((scan_tile[1] - terrain._cast.max) / scan_direction[1])

    scan_tile += scan_direction * max([x_scalar, y_scalar, z_scalar])

    #main loop through grid
    while searching:

        #determines indexes required from grid
        scan_x = int(floor(scan_tile[0]))
        scan_z = int(floor(scan_tile[2]))
        if scan_tile[0] == scan_x and scan_direction[0] < 0:
            scan_x -= 1
            scan_x = max(scan_x, 0)

        if scan_tile[2] == scan_z and scan_direction[2] < 0:
            scan_z -= 1
            scan_z = max(scan_z, 0)

        current_iterations += 1

        #failure cases
        if current_iterations == iterations:
            searching = False
        elif scan_x >= len(height_values):
            searching = False
        elif scan_z >= len(height_values[0]):
            searching = False
        elif scan_x < 0:
            searching = False
        elif scan_z < 0:
            searching = False
        elif scan_tile[1] > terrain._cast.max + 1:
            searching = False
        elif scan_tile[1] < terrain._cast.min - 1:
            searching = False
        elif ursina_distance(scan_tile, original_tile) > scan_max_distance:
            searching = False

        if not searching:
            break

        if calculate_normals:
            start, normal = terrain._cast.prepared_height_values[scan_x][scan_z][sub_face]
        else:
            start, normal = _terraincast_get_plane(terrain, scan_x, scan_z, sub_face)

        bottom_dot = dot(scan_direction, normal)
        top_dot = dot(start - original_tile, normal)
        if bottom_dot != 0:
            magnitude = top_dot / bottom_dot
        elif top_dot == 0:
            magnitude = 0
        else:
            magnitude = None

        if magnitude is not None:
            point = original_tile + magnitude * scan_direction
        else:
            magnitude = 0
            point = Vec3(scan_x + 2, 0, scan_z + 2)

        in_front = magnitude >= 0
        correct_sub_triangle = (point[0] % 1 <= point[2] % 1) == sub_face or point[0] % 1 == point[2] % 1
        x_tolerance = abs(point[0] - scan_x - 0.5) <= 0.5
        z_tolerance = abs(point[2] - scan_z - 0.5) <= 0.5
        #success case
        if in_front and correct_sub_triangle and x_tolerance and z_tolerance:
            break

        elif sub_face:
            # works out next "tile" to move to
            if scan_direction[0] > 0:
                x_scalar = (1 - scan_tile[0] % 1) / scan_direction[0]
            elif scan_direction[0] < 0:
                corrected = (-scan_tile[0]) % 1
                x_scalar = abs((1 - corrected) / scan_direction[0])
            else:
                x_scalar = None

            if scan_direction[2] > 0:
                z_scalar = (1 - scan_tile[2] % 1) / scan_direction[2]
            elif scan_direction[2] < 0:
                corrected = (-scan_tile[2]) % 1
                z_scalar = abs((1 - corrected) / scan_direction[2])
            else:
                z_scalar = None

            if x_scalar is not None and (z_scalar is None or x_scalar < z_scalar):
                scan_tile += x_scalar * scan_direction
            elif z_scalar is not None:
                scan_tile += z_scalar * scan_direction
            else:
                searching = False
                break

        sub_face = not sub_face

    if debug:
        #generates bounding box
        l = -0.5 * terrain._cast.correction_scale - terrain.origin[0]
        r = 0.5 * terrain._cast.correction_scale - terrain.origin[0]

        f = 0.5 * terrain._cast.aspect_ratio * terrain._cast.correction_scale - terrain.origin[2]
        b = -0.5 * terrain._cast.aspect_ratio * terrain._cast.correction_scale - terrain.origin[2]

        u = terrain._cast.max - terrain.origin[1]
        d = terrain._cast.min - terrain.origin[1]

        verts = (
            Vec3(l, d, b), Vec3(r, d, b), Vec3(r, u, b), Vec3(l, u, b),
            Vec3(l, d, f), Vec3(r, d, f), Vec3(r, u, f), Vec3(l, u, f)
        )

        tris = (
            (0, 1, 2, 3), (5, 4, 7, 6),  # forward, back
            (3, 2, 6, 7), (4, 5, 1, 0),  # up, down
            (1, 5, 6, 2), (4, 0, 3, 7)  # right, left
        )
        cube = Mesh(verts, tris)
        terrain._cast.bound.model = cube
        terrain._cast.bound.model.generate()
    if searching:
        #geneartess hit info and undoes some transformations
        point = Vec3(point[0] / terrain._cast.width,
                     point[1],
                     point[2] / terrain._cast.width)

        point -= Vec3(0.5, 0, 0.5 * terrain._cast.aspect_ratio)

        point[0] = point[0] * terrain._cast.correction_scale
        point[2] = point[2] * terrain._cast.correction_scale
        terrain._cast.position = point
        terrain._cast.position -= terrain.origin

        terrain._cast.visible = debug

        terrain._cast.direction.position = normal / terrain._cast.correction_scale

        hit = HitInfo(hit=True)
        hit.point = point
        hit.world_point = terrain._cast.world_position

        hit.normal = Vec3(*normal)
        hit.world_normal = terrain._cast.direction.world_position - terrain.world_position
        hit.distance = ursina_distance(origin, hit.world_point)
        hit.entity = terrain
        hit.entities = [terrain, ]
        hit.hits = [True, ]
        if hit.distance > distance:
            hit = HitInfo(hit=False)
        return hit
    else:
        terrain._cast.visible = False

        hit = HitInfo(hit=False)
        return hit


if __name__ == '__main__':
    app = Ursina()

    terrainEntity = Entity(model=Terrain('heightmap_1', skip=8),
                           scale=(20, 5, 20),
                           rotation=(30, 40, 50),
                           origin=(1, 1, 1),
                           texture='heightmap_1')

    hit_entity = Entity(model='sphere', scale=0.1)
    EditorCamera()


    def update():
        hit = terraincast(camera.world_position, terrainEntity, direction=camera.forward, debug=True)
        if hit:
            hit_entity.position = hit.world_point + hit.world_normal

            hit.entity.rotation_y += 2*time.dt

    Sky()
    app.run()
