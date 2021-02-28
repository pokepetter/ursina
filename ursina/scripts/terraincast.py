from ursina import  * 
from math import radians, sin, cos
from ursina.hit_info import HitInfo
from numpy import cross, dot
# # BUG[should be fixed 28 / 2 / 21]: doesn't work correctly when the terrain entity is rotated on the y axis

def terraincast(origin, terrain): # mainly used for getting the y position on a terrain. returns a HitInfo like raycast()
    

    
    origin = Vec3(*origin)
    height_values = terrain.model.height_values
    width = terrain.model.width
    depth = terrain.model.depth
    height_multiplier = terrain.world_scale_y

    if terrain.world_rotation[0] != 0 or terrain.world_rotation[2] != 0:
        print("terraincaster does not work when the terrain is rotated to not face upwards")
        return None

    #stores x,z to reduce unecessary calculations later
    point_x = origin[0]
    point_z = origin[2]


    #transformations processed for origin to align with height_values
    angle =  - radians(terrain.world_rotation_y)
    origin_vector = origin - terrain.world_position

    store = origin_vector[0]
    origin_vector[0] = origin_vector[0] * cos( - angle) - origin_vector[2] * sin( - angle)
    origin_vector[2] = store * sin( - angle) + origin_vector[2] * cos( - angle)
    origin = terrain.world_position + origin_vector
    
    
    origin = (origin - terrain.world_position + terrain.origin * terrain.world_scale)
    origin[0] = (origin[0] / terrain.world_scale_x + .5) * width
    origin[2] = (origin[2] / terrain.world_scale_z + .5) * width
    



    if origin[0] >=0 and origin[0] < len(height_values) and origin[2] >=0 and origin[2] < len(height_values[0]):
        if floor(origin[2]) == len(height_values[0]) - 1 and floor(origin[0]) == len(height_values) - 1:
            start = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2]))
            normal = Vec3(0,1,0)
        else:
            if floor(origin[2]) == len(height_values[0]) - 1:
                start = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2]))
                right = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2] + 1))
                left = Vec3(floor(origin[0] + 1),height_values[int(floor(origin[0]) + 1)][int(floor(origin[2]))],floor(origin[2] + 1))
            elif floor(origin[0]) == len(height_values) - 1:
                start = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2]))
                right = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]) + 1)],floor(origin[2]) + 1)
                left = Vec3(floor(origin[0] + 1),height_values[int(floor(origin[0]))][int(floor(origin[2]) + 1)],floor(origin[2] + 1))
                
                
            #determines which triangle of the current square the player is standing on and gets vectors for each corner
            elif origin[0] % 1 < origin[2] % 1:
                start = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2]))
                right = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]) + 1)],floor(origin[2]) + 1)
                left = Vec3(floor(origin[0] + 1),height_values[int(floor(origin[0]) + 1)][int(floor(origin[2]) + 1)],floor(origin[2] + 1))
            else:
                start = Vec3(floor(origin[0]),height_values[int(floor(origin[0]))][int(floor(origin[2]))],floor(origin[2]))
                right = Vec3(floor(origin[0]) + 1,height_values[int(floor(origin[0]) + 1)][int(floor(origin[2]))],floor(origin[2]))
                left = Vec3(floor(origin[0] + 1),height_values[int(floor(origin[0]) + 1)][int(floor(origin[2]) + 1)],floor(origin[2] + 1))

            #get normal to face and make sure it's facing up and is 1 unit in length
            normal = cross(left - start,right - start)
            if normal[1] <0:
                normal =  - normal
            normal = normal / sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)

        hit = HitInfo(hit=True)                                                                                          
        #finds point where verticle line from origin and face plane intersect based on the calculated normal this uses the maths that is here for anyone interested https: /  / en.wikipedia.org / wiki / Line - plane_intersection
        hit.world_point = Vec3(point_x,
                             (dot(start,normal) - origin[0] * normal[0] - origin[2] * normal[2]) / normal[1] * terrain.world_scale_y + terrain.world_position[1] - terrain.origin[1] * terrain.world_scale_y,
                             point_z
        )

        #finishes up setting hit info object
        if hasattr(terrain.parent, 'position'):
            hit.point = hit.world_point - terrain.parent.world_position
        else:
            hit.point = hit.world_point
            #parented to scene or something so reverts to world coordinates
        hit.normal = Vec3(*normal)
        hit.world_normal = hit.normal
        hit.distance = origin[1] - hit.world_point[1]
        hit.entity = terrain
        hit.entities = [terrain, ]
        hit.hits = [True, ]
        return hit
    else:
        hit = HitInfo(hit=False, distance=inf)
        return hit




if __name__ == '__main__':
    app = Ursina()
    application.asset_folder = Path('.').parent.parent / 'samples'
    terrain = Entity(model = Terrain('heightmap_1', skip=16), scale=(20,5,20), rotation=(0,45,0), origin=( - 0.1, - 0.1, - 0.1), texture='heightmap_1')
    player = Entity(model='cube', origin_y= - 0.5, scale=0.1, color=color.orange)

    def update():
        player.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
        player.z += (held_keys['w'] - held_keys['s']) * time.dt * 5

        hit_info = terraincast(player.world_position, terrain)
        if hit_info.hit:
            player.y = hit_info.world_point.y



    EditorCamera()
    Sky()
    app.run()
