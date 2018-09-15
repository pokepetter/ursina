from ursina import *

class SmoothFollow(object):

    def __init__(self, target=None, offset=(0,0,0), speed=8):
        self.target = target
        self.offset = offset
        self.speed = speed


    def update(self):
        if not self.target:
            return

        self.entity.position = lerp(
            self.entity.position,
            self.target.position + self.offset,
            time.dt * self.speed)



if __name__ == '__main__':
    app = Ursina()

    class Player(Entity):
        def __init__(self):
            super().__init__(model='cube', color=color.orange)

        def update(self):
            self.x += held_keys['d'] * .1
            self.x -= held_keys['a'] * .1

    player = Player()
    Entity(model='cube').add_script(SmoothFollow(target=player, offset=(0,2,0)))
    app.run()
