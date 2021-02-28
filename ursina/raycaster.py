import sys

from ursina import *
from ursina.entity import Entity
from ursina.mesh import Mesh
from ursina.scene import instance as scene
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionSegment, CollisionBox
from ursina.vec3 import Vec3
from math import sqrt, inf
from ursina.hit_info import HitInfo


class Raycaster(Entity):
    line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')


    def __init__(self):
        super().__init__(
            name = 'raycaster',
            eternal = True
            )
        self._picker = CollisionTraverser()  # Make a traverser
        self._pq = CollisionHandlerQueue()  # Make a handler
        self._pickerNode = CollisionNode('raycaster')
        self._pickerNode.set_into_collide_mask(0)
        self._pickerNP = self.attach_new_node(self._pickerNode)
        self._picker.addCollider(self._pickerNP, self._pq)


    def distance(self, a, b):
        return sqrt(sum( (a - b)**2 for a, b in zip(a, b)))


    def raycast(self, origin, direction=(0,0,1), distance=inf, traverse_target=scene, ignore=list(), debug=False):
        self.position = origin
        self.look_at(self.position + direction)

        self._pickerNode.clearSolids()
        ray = CollisionRay()
        ray.setOrigin(Vec3(0,0,0))
        ray.setDirection(Vec3(0,0,1))

        self._pickerNode.addSolid(ray)

        if debug:
            temp = Entity(position=origin, model=Raycaster.line_model, scale=Vec3(1,1,min(distance,9999)), add_to_scene_entities=False)
            temp.look_at(self.position + direction)
            destroy(temp, 1/30)

        self._picker.traverse(traverse_target)

        if self._pq.get_num_entries() == 0:
            self.hit = HitInfo(hit=False, distance=distance)
            return self.hit

        ignore += tuple([e for e in scene.entities if not e.collision])

        self._pq.sort_entries()
        self.entries = [        # filter out ignored entities
            e for e in self._pq.getEntries()
            if e.get_into_node_path().parent not in ignore
            and self.distance(self.world_position, Vec3(*e.get_surface_point(render))) <= distance
            ]

        if len(self.entries) == 0:
            self.hit = HitInfo(hit=False, distance=distance)
            return self.hit

        self.collision = self.entries[0]
        nP = self.collision.get_into_node_path().parent
        point = Vec3(*self.collision.get_surface_point(nP))
        world_point = Vec3(*self.collision.get_surface_point(render))
        hit_dist = self.distance(self.world_position, world_point)


        self.hit = HitInfo(hit=True, distance=distance)
        for e in scene.entities:
            if e == nP:
                self.hit.entity = e

        nPs = [e.get_into_node_path().parent for e in self.entries]
        self.hit.entities = [e for e in scene.entities if e in nPs]

        self.hit.point = point
        self.hit.world_point = world_point
        self.hit.distance = hit_dist

        self.hit.normal = Vec3(*self.collision.get_surface_normal(self.collision.get_into_node_path().parent).normalized())
        self.hit.world_normal = Vec3(*self.collision.get_surface_normal(render).normalized())
        return self.hit

        self.hit = HitInfo(hit=False, distance=distance)
        return self.hit


    def boxcast(self, origin, direction=(0,0,1), distance=9999, thickness=(1,1), traverse_target=scene, ignore=list(), debug=False): # similar to raycast, but with width and height
        if isinstance(thickness, (int, float, complex)):
            thickness = (thickness, thickness)

        temp = Entity(
            position=origin,
            model='cube',
            origin_z=-.5,
            scale=Vec3(abs(thickness[0]), abs(thickness[1]), abs(distance)),
            collider='box',
            color=color.white33,
            always_on_top=debug,
            visible=debug
            )
        temp.look_at(origin + direction)
        hit_info = temp.intersects(traverse_target=traverse_target, ignore=ignore)
        if hit_info.world_point:
            hit_info.distance = ursinamath.distance(origin, hit_info.world_point)
        else:
            hit_info.distance = distance

        if debug:
            temp.collision = False
            temp.scale_z = hit_info.distance
            destroy(temp, delay=.2)
        else:
            destroy(temp)

        return hit_info
    def terrainCast(self,origin,terrain):
        terrainEntity=terrain
        origin=Vec3(origin)
        height_values=terrainEntity.model.height_values
        width=terrainEntity.model.width
        depth=terrainEntity.model.depth
        heightMultiplier=terrainEntity.world_scale_y

        if terrainEntity.world_rotation[0] != 0 or terrainEntity.world_rotation[2] != 0:
            print("terrainCaster does not work when the terrain is rotated to not face upwards")
            return None

        #stores x,z to reduce uneccesary calculations later
        pointX=origin[0]
        pointZ=origin[2]


        #transformations processed for origin to align with height_values
        angle=-radians(terrainEntity.world_rotation_y)
        originVector=origin-terrainEntity.world_position

        store=originVector[0]
        originVector[0]=originVector[0]*cos(-angle) - originVector[2]*sin(-angle)
        originVector[2]=store*sin(-angle) + originVector[2]*cos(-angle)
        origin=terrainEntity.world_position+originVector
        
        
        origin=(origin-terrainEntity.world_position+terrainEntity.origin*terrainEntity.world_scale)
        origin[0]=(origin[0]/terrainEntity.world_scale_x+.5)*width
        origin[2]=(origin[2]/terrainEntity.world_scale_z+.5)*width
        

        #aligns coordinates to match height array/useful in bug fixing and stuff
        xOffset=0
        zOffset=0

        if origin[0] >=0 and origin[0] < len(height_values)-1 and origin[2] >=0 and origin[2] < len(height_values[0])-1:
            #determines which triangle of the current square the player is standing on and gets vectors for each corner
            if origin[0] % 1 < origin[2] % 1:
                start=Vec3(floor(origin[0]),height_values[int(floor(origin[0]))+xOffset][int(floor(origin[2]))+zOffset],floor(origin[2]))
                right=Vec3(floor(origin[0]),height_values[int(floor(origin[0]))+xOffset][int(floor(origin[2])+1)+zOffset],floor(origin[2])+1)
                left=Vec3(floor(origin[0]+1),height_values[int(floor(origin[0])+1)+xOffset][int(floor(origin[2])+1)+zOffset],floor(origin[2]+1))
            else:
                start=Vec3(floor(origin[0]),height_values[int(floor(origin[0]))+xOffset][int(floor(origin[2]))+zOffset],floor(origin[2]))
                right=Vec3(floor(origin[0])+1,height_values[int(floor(origin[0])+1)+xOffset][int(floor(origin[2]))+zOffset],floor(origin[2]))
                left=Vec3(floor(origin[0]+1),height_values[int(floor(origin[0])+1)+xOffset][int(floor(origin[2])+1)+zOffset],floor(origin[2]+1))

            #get normal to face and make sure it's facing up and is 1 unit in length
            normal=cross(left-start,right-start)
            if normal[1] <0:
                normal=-normal
            normal=normal/sqrt(normal[0]**2+normal[1]**2+normal[2]**2)

            hit=HitInfo(hit=True)                                                                                          
            #finds point where verticle line from origin and face plane intersect based on the calculated normal this uses the maths that is here for anyone interested https://en.wikipedia.org/wiki/Line-plane_intersection
            hit.world_point=Vec3(pointX,(dot(start,normal)-origin[0]*normal[0]-origin[2]*normal[2])/normal[1]*terrainEntity.world_scale_y+terrainEntity.world_position[1]-terrainEntity.origin[1]*terrainEntity.world_scale_y,pointZ)

            #finishes up setting hit info object
            if hasattr(terrainEntity.parent,"position"):
                hit.point=hit.world_point-terrainEntity.parent.world_position
            else:
                hit.point=hit.world_point
                #parented to scene or something so reverts to world coordinates
            hit.normal=Vec3(normal[0],normal[1],normal[2])
            hit.world_normal=hit.normal
            hit.distance=origin[1]-hit.world_point[1]
            hit.entity=terrainEntity
            hit.entities=[terrainEntity]
            hit.hits=[True]
                                                                                              


            return hit
        else:
            hit = HitInfo(hit=False,distance=inf)
            return hit

instance = Raycaster()
sys.modules[__name__] = instance




if __name__ == '__main__':
    app = Ursina()

    '''
    Casts a ray from *origin*, in *direction*, with length *distance* and returns
    a HitInfo containing information about what it hit. This ray will only hit entities with a collider.

    Use optional *traverse_target* to only be able to hit a specific entity and its children/descendants.
    Use optional *ignore* list to ignore certain entities.
    Setting debug to True will draw the line on screen.

    Example where we only move if a wall is not hit:
    '''


    class Player(Entity):

        def update(self):
            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                ).normalized()  # get the direction we're trying to walk in.

            origin = self.world_position + (self.up*.5) # the ray should start slightly up from the ground so we can walk up slopes or walk over small objects.
            hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
            if not hit_info.hit:
                self.position += self.direction * 5 * time.dt

    Player(model='cube', origin_y=-.5, color=color.orange)
    wall_left = Entity(model='cube', collider='box', scale_y=3, origin_y=-.5, color=color.azure, x=-4)
    wall_right = duplicate(wall_left, x=4)
    camera.y = 2
    app.run()

    # test
    breakpoint()
    d = Entity(parent=scene, position=(0,0,2), model='cube', color=color.orange, collider='box', scale=2)
    e = Entity(model='cube', color=color.lime)

    camera.position = (0, 15, -15)
    camera.look_at(e)
    # camera.reparent_to(e)
    speed = .01
    rotation_speed = 1
    intersection_marker = Entity(model='cube', scale=.2, color=color.red)

    def update():
        e.position += e.forward * held_keys['w'] * speed
        e.position += e.left * held_keys['a'] * speed
        e.position += e.back * held_keys['s'] * speed
        e.position += e.right * held_keys['d'] * speed

        e.rotation_y -= held_keys['q'] * rotation_speed
        e.rotation_y += held_keys['e'] * rotation_speed

        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        ray = boxcast(e.world_position, e.right, 3, debug=True)
        # print(ray.distance, ray2.distance)
        intersection_marker.world_position = ray.world_point
        intersection_marker.visible = ray.hit
        if ray.hit:
            d.color = color.azure
        else:
            d.color = color.orange

    t = time.time()
    # ray = raycast(e.world_position, e.forward, 3, debug=True)
    print(time.time() - t)
    # raycast((0,0,-2), (0,0,1), 5, debug=False)

    EditorCamera()
    app.run()
