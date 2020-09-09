from ursina import *


class CollisionZone(Entity):
    def __init__(self, radius=2, target_entities=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.entities_with_mesh_colliders = target_entities
        if not self.entities_with_mesh_colliders:
            self.entities_with_mesh_colliders = [e for e in scene.entities if isinstance(e.collider, MeshCollider)]

        self._t = 0
        self._update_rate = .25
        self._prev_pos = self.world_position


    def update(self):
        self._t += time.dt
        if self._t < self._update_rate:
            return

        self._t = 0

        # only update after we've moved a certain distance
        if distance_xz(self.world_position, self._prev_pos) < self.radius/2:
            return
        else:
            self._prev_pos = self.world_position


        for e in self.entities_with_mesh_colliders:
            e.collider.node.clearSolids()
            for tri in e.collider.collision_polygons:
                if (distance_xz(self.get_position(e), tri.getPoint(0)) < self.radius
                or distance_xz(self.get_position(e), tri.getPoint(1)) < self.radius
                or distance_xz(self.get_position(e), tri.getPoint(2)) < self.radius):
                    e.collider.node.addSolid(tri)



if __name__ == '__main__':
    '''
    This will only enable mesh colliders' collision polygons within a certain range,
    in order to improve performance. 
    '''

    from ursina.shaders import basic_lighting_shader
    window.vsync = False
    app = Ursina()

    application.asset_folder = application.asset_folder.parent
    terrain = Entity(model='heightmap_test', scale=1, texture='grass', collider='mesh', shader=basic_lighting_shader)
    collision_zone = CollisionZone(model='cube', scale=.1)


    def input(key):
        if key == 'c':
            terrain.collision = not terrain.collision


    def update():
        collision_zone.x += (held_keys['d'] - held_keys['a']) * time.dt * 2
        collision_zone.z += (held_keys['w'] - held_keys['s']) * time.dt * 2

        hit_info = raycast(collision_zone.world_position+Vec3(0,2,0), Vec3(0,-1,0))
        if hit_info.hit:
            collision_zone.y = hit_info.world_point.y

    Sky()
    EditorCamera(position=(0,0,0))

    app.run()
