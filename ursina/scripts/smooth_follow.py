from ursina import *

class SmoothFollow():

    def __init__(self, target=None, offset=(0,0,0), speed=8, rotation_speed=0, rotation_offset=(0,0,0)):
        self.target = target
        self.offset = offset
        self.speed = speed

        self.rotation_speed = rotation_speed
        self.rotation_offset = rotation_offset


    def update(self):
        if not self.target:
            return

        self.entity.world_position = lerp(
            self.entity.world_position,
            self.target.world_position + Vec3(*self.offset),
            time.dt * self.speed)

        if self.rotation_speed > 0:
            self.entity.world_rotation = lerp(
                self.entity.world_rotation,
                self.target.world_rotation + self.rotation_offset,
                time.dt * self.rotation_speed)




if __name__ == '__main__':
    app = Ursina()

    player = Entity(model='cube', color=color.orange)

    def update():
        player.x += held_keys['d'] * .1
        player.x -= held_keys['a'] * .1

    e = Entity(model='cube')
    sf = e.add_script(SmoothFollow(target=player, offset=(0,2,0)))

    def input(key):
        global sf
        if key == '1' and sf in e.scripts:
            e.scripts.remove(sf)

    EditorCamera()
    app.run()
