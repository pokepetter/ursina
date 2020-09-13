from ursina import *


class CollisionZone(Entity):
    def __init__(self, radius=2, target_entities=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.entities_with_mesh_colliders = target_entities # defaults to all entities with a mesh collider
        if not self.entities_with_mesh_colliders:
            self.entities_with_mesh_colliders = [e for e in scene.entities if isinstance(e.collider, MeshCollider)]

        self._update_rate = .25
        self._t = self._update_rate
        self._prev_pos = self.world_position
        # self.debug = False
        # self.debug_parent = Entity(ignore=True)
        for e in self.entities_with_mesh_colliders:
            e.collider.node.clearSolids()
        self.update_colliders()


    def update(self):
        self._t += time.dt
        if self._t < self._update_rate:
            return

        self._t = 0

        # only update after we've moved a certain distance
        if distance_xz(self.world_position, self._prev_pos) < self.radius / 2:
            return

        self._prev_pos = self.world_position
        self.update_colliders()


    def update_colliders(self):
        # if self.debug:
        #     destroy(self.debug_parent)
        # self.debug_parent = Entity(ignore=True)


        for e in self.entities_with_mesh_colliders:
            # if self.debug:
            #     # print('debug')
            #     debug_model = Entity(
            #         parent=self.debug_parent,
            #         world_position=e.world_position,
            #         world_scale=e.world_scale,
            #         model=Mesh(mode='line', static=False),
            #         color=color.red,
            #         always_on_top=True
            #     ).model
            #     for tri in e.collider.collision_polygons:
            #         if (distance_xz(self.get_position(e), tri.getPoint(0)) < self.radius / e.world_scale_x
            #         or distance_xz(self.get_position(e), tri.getPoint(1)) < self.radius / e.world_scale_x
            #         or distance_xz(self.get_position(e), tri.getPoint(2)) < self.radius / e.world_scale_x):
            #             if self.debug:
            #                 debug_model.vertices.extend([tri.getPoint(2), tri.getPoint(1), tri.getPoint(0)])
            #
            #     # debug_model.generate()


            e.collider.node.clearSolids()
            i = 0
            for tri in e.collider.collision_polygons:
                if (distance_xz(self.get_position(e), tri.getPoint(0)) < self.radius / e.world_scale_x
                or distance_xz(self.get_position(e), tri.getPoint(1)) < self.radius / e.world_scale_x
                or distance_xz(self.get_position(e), tri.getPoint(2)) < self.radius / e.world_scale_x):
                    # e.collider.node.addSolid(tri)
                    invoke(e.collider.node.addSolid, tri, delay=i*.01)
                    i+= 1


if __name__ == '__main__':
    '''
    This will only enable mesh colliders' collision polygons within a certain range,
    in order to improve performance.
    '''

    from ursina.shaders import basic_lighting_shader
    window.vsync = False
    app = Ursina()

    application.asset_folder = application.asset_folder.parent
    terrain = Entity(model='heightmap_test', scale=32, texture='grass', collider='mesh', shader=basic_lighting_shader)
    from ursina.prefabs.first_person_controller import FirstPersonController
    player = FirstPersonController(speed=10)
    collision_zone = CollisionZone(parent=player, radius=32)


    def input(key):
        if key == 'c':
            terrain.collision = not terrain.collision


    # def update():
    #     collision_zone.x += (held_keys['d'] - held_keys['a']) * time.dt * 2
    #     collision_zone.z += (held_keys['w'] - held_keys['s']) * time.dt * 2
    #
    #     hit_info = raycast(collision_zone.world_position+Vec3(0,2,0), Vec3(0,-1,0))
    #     if hit_info.hit:
    #         collision_zone.y = hit_info.world_point.y

    Sky()
    # EditorCamera(position=(0,0,0))
    base.set_frame_rate_meter(True)
    app.run()
