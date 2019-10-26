from ursina import *

class Scrollable():

    def __init__(self, **kwargs):
        super().__init__()
        self.max = math.inf
        self.min = -math.inf
        self.scroll_speed = .1
        self.direction = (0,1,0)

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        value = Vec3(value[0], value[1], value[2] if len(value) == 3 else 0)
        self._direction = value


    def input(self, key):
        if not mouse.hovered_entity:
            # print('pass', mouse.hovered_entity)
            return

        if self.entity.hovered or mouse.hovered_entity.has_ancestor(self.entity):
            # print(key)
            if key == 'scroll up':
                self.entity.position -= self.direction * self.scroll_speed
            if key == 'scroll down':
                self.entity.position += self.direction * self.scroll_speed

            self.entity.y = max(min(self.entity.y, self.max), self.min)


if __name__ == '__main__':
    app = Ursina()
    p = Panel(scale=(.4, .8), collider='box')
    p.add_script(Scrollable())
    app.run()
