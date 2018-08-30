from ursina import *

class Scrollable(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max = math.inf
        self.min = -math.inf
        self.scroll_speed = .1
        self.direction = (0,1,0)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        value = Vec3(value[0], value[1], value[2] if len(value) == 3 else 0)
        self._direction = value


    def input(self, key):

        if self.hovered:
            print(key)
            if key == 'scroll up':
                self.position -= self.direction * self.scroll_speed
            if key == 'scroll down':
                self.position += self.direction * self.scroll_speed

            self.y = max(min(self.y, self.max), self.min)


if __name__ == '__main__':
    app = Ursina()
    Scrollable()
    app.run()
