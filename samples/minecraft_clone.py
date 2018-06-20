from ursina import *


class MinecraftClone(Entity):

    def __init__(self):
        super().__init__('minecraft_clone')

        for z in range(32):
            for x in range(32):
                for y in range(1):
                    voxel = Voxel()
                    voxel.name = 'voxel_' + str(x) + '_' + str(z)
                    voxel.parent = self
                    voxel.position = (x, y, z)

        sky = load_prefab('sky')
        # load_prefab('button')

        player = FirstPersonController()
        player.parent = self


class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'voxel'
        self.model = 'cube'
        # self.origin = (0, .5, 0)
        self.collider = 'box'
        self.texture = 'white_cube'
        self.color = color.color(0, 0, random.uniform(.9, 1.0))


    def input(self, key):
        # if not scene.editor or scene.editor.enabled:
        #     return
        if self.hovered:
            if key == 'left mouse down' and self.hovered:
                voxel = Voxel()
                voxel.parent = self.parent
                voxel.position = self.position + mouse.normal
                # test_model = loader.load('cube.egg')
                # test_model.reparent_to(voxel.collider.node_path)
                # test_model.setPos(Vec3(0,0,0))
                # test_model.set_color_scale(color.red)
                # test_model.set_scale(1.05)

            if key == 'right mouse down':
                destroy(self)


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .1

        self.i = 0
        self.update_interval = 30

        cursor = Panel()
        cursor.color = color.light_gray
        cursor.scale *= .008
        cursor.rotation_z = 45
        if not scene.editor:
            self.start()

        self.graphics = Entity('player_graphics')
        self.graphics.parent = self
        self.graphics.model = 'cube'
        self.graphics.color = color.orange
        self.graphics.origin = (0, -.5, 0)
        self.graphics.scale = (1, 1.8, 1)

        self.arrow = Entity()
        self.arrow.parent = self.graphics
        self.arrow.model = 'cube'
        self.arrow.color = color.blue
        self.arrow.position = (0, .5, .5)
        self.arrow.scale = (.1, .1, .5)


    def start(self):
        camera.parent = self
        self.position = (0, .5, 1)
        # camera.position = (0, 4, -4)
        camera.rotation = (0,0,0)
        camera.position = (0,2,0)
        camera.fov = 90
        mouse.locked = True


    def update(self, dt):
        # camera.position = self.position + (0, 4, -4)


        # raycast(self.world_position, camera.forward, 100, render, debug=True)
        if self.i < self.update_interval:
            self.i += 1
            return

        # if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        #     self.moving = True


        if held_keys['w']:
            if not raycast(self.world_position + self.up, self.forward, 1, scene):
                self.position += self.forward * held_keys['w'] * self.speed
        if held_keys['s']:
            if not raycast(self.world_position + self.up, self.back, 1, scene):
                self.position += self.back * held_keys['s'] * self.speed
        if held_keys['d']:
            if not raycast(self.world_position + self.up, self.right, 1, scene):
                self.position += self.right * held_keys['d'] * self.speed
        if held_keys['a']:
            if not raycast(self.world_position + self.up, self.left, 1, scene):
                self.position += self.left * held_keys['a'] * self.speed
        # self.position += self.up * held_keys['e'] * self.speed
        # self.position += self.down * held_keys['q'] * self.speed
        # mag = max(x, z);

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

if __name__ == '__main__':
    app = main.Ursina()
    # destroy(scene)
    # app.scene = MinecraftClone()
    load_scene(MinecraftClone)
    # scene.name = 'minecraft_clone_scene'
    app.run()
