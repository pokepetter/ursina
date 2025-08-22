from ursina import Vec3, lerp_exponential_decay, time



class SmoothFollow:
    def __init__(self, target=None, offset=Vec3.zero, speed=8, rotation_speed=0, rotation_offset=Vec3.zero):
        self.target = target
        self.offset = Vec3(*offset)
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.rotation_offset = rotation_offset


    def update(self):
        if not self.target:
            return

        self.entity.world_position = lerp_exponential_decay(self.entity.world_position, self.target.world_position+self.offset, time.dt*self.speed)

        if self.rotation_speed > 0:
            self.entity.world_rotation = lerp_exponential_decay(self.entity.world_rotation, self.target.world_rotation+self.rotation_offset, time.dt*self.rotation_speed)


if __name__ == '__main__':
    from ursina import Ursina, Entity, EditorCamera, color, held_keys
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
