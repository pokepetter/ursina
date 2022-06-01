from ursina.entity import Entity
from ursina.ursinamath import distance
import time

# TODO:
# circle
# AArectangle
# AAbox
# box

# sphere

class Trigger(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.trigger_targets = None
        self.radius = .5
        self.triggerers = []
        self.update_rate = 4
        self._i = 0

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self._i += 1
        if self._i < self.update_rate:
            return

        self._i = 0

        for other in self.trigger_targets:
            if other == self:
                continue

            dist = distance(other, self)
            if not other in self.triggerers and dist <= self.radius:
                self.triggerers.append(other)
                if hasattr(self, 'on_trigger_enter'):
                    self.on_trigger_enter()
                continue

            if other in self.triggerers and dist > self.radius:
                self.triggerers.remove(other)
                if hasattr(self, 'on_trigger_exit'):
                    self.on_trigger_exit()
                continue

            if other in self.triggerers and hasattr(self, 'on_trigger_stay'):
                self.on_trigger_stay()




if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    player = Entity(model='cube', color=color.azure, scale=.05)
    def update():
        player.x += held_keys['d'] * time.dt * 2
        player.x -= held_keys['a'] * time.dt * 2

    t = Trigger(trigger_targets=(player,), x=1, model='sphere', color=color.color(0,1,1,.5))
    t.on_trigger_enter = Func(print, 'enter')
    t.on_trigger_exit =  Func(print, 'exit')
    t.on_trigger_stay =  Func(print, 'stay')

    app.run()
