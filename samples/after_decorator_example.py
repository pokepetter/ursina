from ursina import *

app = Ursina()

class Player(Entity):
    @every(1/30)
    def fixed_update(self):
        print('-')

    @every(.5)
    def slow_update(self):
        print('s')


class Enemy(Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'enemy'

    @every(1)
    def attack(self):
        print('attack!', self)

player = Player()
player_2 = Player(name='player_2')
enemy = Enemy()
enemy = Enemy()
enemy = Enemy()


def input(key):
    if key == 'd':
        destroy(enemy)
        for e in every.decorated_methods:
            print('--', e._func)

        print(enemy.animations)



app.run()
