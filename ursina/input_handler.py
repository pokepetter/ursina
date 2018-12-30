import sys
from collections import defaultdict


class InputHandler():

    def __init__(self):
        self.control = False
        self.left_control = False
        self.right_control = False

        self.shift = False
        self.left_shift = False
        self.right_shift = False

        self.alt = False
        self.left_alt = False
        self.right_alt = False

        self.held_keys = defaultdict(lambda: 0)
        self.rebinds = dict()


    def bind(self, alternative_key, original_key):
        self.rebinds[original_key] = alternative_key

    def unbind(self, key):
        if key in self.rebinds:
            del self.rebinds[key]
        else:
            self.rebinds[key] = 'none'

    def rebind(self, from_key, to_key):
        self.unbind(to_key)
        self.bind(to_key, from_key)


    def input(self, key):
        if key == 'arrow up':
            self.held_keys[key] = 1
            return
        elif key == 'arrow up up':
            self.held_keys['arrow up'] = 0
            return

        if key.endswith('up'):
            self.held_keys[key[:-3]] = 0
        else:
            self.held_keys[key] = 1



sys.modules[__name__] = InputHandler()
