from ursina import *


class Animator():
    def __init__(self, animations=None, start_state=''):

        self.animations = animations    # dict

        if not start_state and self.animations:
            start_state = list(self.animations)[0]

        self.start_state = start_state
        self._state = None
        self.state = start_state



    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):

        if not value in self.animations:
            print(self, 'has no animation:', value)

        elif not self._state == value:
            # only show set state and disable the rest
            for key, anim in self.animations.items():
                if anim:
                    anim.enabled = value == key

            anim = self.animations[value]
            if hasattr(anim, 'start') and callable(anim.start):
                # print('start', anim)
                anim.start()

        self._state = value




if __name__ == '__main__':
    app = Ursina()
    # texture_importer.textureless=True
    anim = Animation('ursina_wink', loop=True, autoplay=False)
    a = Animator(
        animations = {
            'lol' : Entity(model='cube', color=color.red),
            'yo' : Entity(model='cube', color=color.green, x=1),
            'help' : anim,
        }
    )
    a.state = 'yo'

    Text('press <red>1<default>, <green>2<default> or <violet>3<default> to toggle different animator states', origin=(0,-.5), y=-.4)

    def input(key):
        if key == '1':
            a.state = 'lol'
        if key == '2':
            a.state = 'yo'
        if key == '3':
            a.state = 'help'
            print(anim.enabled)

    app.run()
